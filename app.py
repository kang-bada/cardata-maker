import streamlit as st
import os
import asyncio
import urllib.request
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

st.set_page_config(page_title="컨텐츠 제작소 - 템플릿 방식", page_icon="🚗")
st.title("🚗 컨텐츠 제작소: 템플릿 기반 자동화")
st.write("미리 준비된 고화질 배경 템플릿 위에 데이터와 자막만 깔끔하게 얹어냅니다.")

# 폰트 세팅 (두꺼운 고딕체)
font_path = "NanumGothic.ttf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf", font_path)

# 1. 템플릿 업로드 영역
st.subheader("1️⃣ 배경 템플릿 업로드")
st.write("캔바(Canva) 등에서 만든 세로형 고화질 배경 이미지(1080x1920)를 올려주세요.")
uploaded_bg = st.file_uploader("배경 이미지 파일 (PNG, JPG)", type=["png", "jpg", "jpeg"])

# 2. 데이터 입력 UI
st.subheader("2️⃣ 이번 달 데이터 입력")
default_data = pd.DataFrame(
    [
        {"순위": "5위", "차종": "기아 스포티지", "판매량": "3,874", "대본": "5위는 3,874대로 기아 스포티지입니다."},
        {"순위": "4위", "차종": "기아 카니발", "판매량": "4,186", "대본": "4위는 4,186대로 아빠들의 로망, 기아 카니발이 차지했습니다."},
        {"순위": "3위", "차종": "현대 더 뉴 그랜저", "판매량": "5,931", "대본": "3위는 5,931대로 현대 그랜저가 세단의 자존심을 지켰습니다."},
        {"순위": "2위", "차종": "기아 쏘렌토", "판매량": "6,397", "대본": "2위는 6,397대로 굳건한 1위 패밀리 SUV, 기아 쏘렌토입니다."},
        {"순위": "1위", "차종": "테슬라 Model Y", "판매량": "9,638", "대본": "대망의 1위는 무려 9,638대, 테슬라 모델 Y입니다! 압도적이네요."}
    ]
)
edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

# 3. 텍스트 오버레이 합성 함수
async def generate_tts(text, path):
    communicate = edge_tts.Communicate(text, "ko-KR-InJoonNeural")
    await communicate.save(path)

def create_overlay_card(bg_image_path, rank, title, count, script, output_path):
    # 업로드된 배경 이미지 열기 (없으면 검은 배경 대체)
    if bg_image_path:
        img = Image.open(bg_image_path).convert("RGB")
        img = img.resize((1080, 1920)) # 쇼츠 규격 강제 맞춤
    else:
        img = Image.new("RGB", (1080, 1920), color=(15, 18, 26))
    
    draw = ImageDraw.Draw(img)
    
    # 폰트 크기 지정
    font_rank = ImageFont.truetype(font_path, 80)
    font_title = ImageFont.truetype(font_path, 110)
    font_count = ImageFont.truetype(font_path, 130)
    font_script = ImageFont.truetype(font_path, 50)
    
    # 중앙 정렬로 텍스트 얹기 (배경 디자인에 맞춰 좌표 수정 가능)
    # 순위
    draw.text((540, 400), f"- {rank} -", font=font_rank, fill=(255, 75, 75) if rank=="1위" else (0, 210, 255), anchor="mm")
    # 차종
    draw.text((540, 580), str(title), font=font_title, fill=(255, 255, 255), anchor="mm")
    # 판매량
    draw.text((540, 800), f"{count} 대", font=font_count, fill=(255, 200, 50), anchor="mm")
    
    # 하단 자막 (가독성을 위해 반투명 검은색 박스 먼저 깔기)
    draw.rounded_rectangle([80, 1550, 1000, 1750], radius=20, fill=(0, 0, 0, 180))
    
    # 자막 자동 줄바꿈
    script_str = str(script)
    if len(script_str) > 22:
        mid_idx = len(script_str) // 2
        space_idx = script_str.find(' ', mid_idx - 5, mid_idx + 5)
        if space_idx == -1: space_idx = mid_idx
        draw.text((540, 1610), script_str[:space_idx].strip(), font=font_script, fill=(255, 255, 255), anchor="mm")
        draw.text((540, 1690), script_str[space_idx:].strip(), font=font_script, fill=(255, 255, 255), anchor="mm")
    else:
        draw.text((540, 1650), script_str, font=font_script, fill=(255, 255, 255), anchor="mm")

    img.save(output_path)

# 4. 렌더링 실행
if st.button("🎬 오버레이 영상 렌더링 시작"):
    with st.spinner("템플릿에 데이터를 합성하여 영상을 제작 중입니다..."):
        os.makedirs("temp", exist_ok=True)
        clips = []
        
        # 업로드된 이미지가 있으면 임시 저장
        bg_path = None
        if uploaded_bg is not None:
            bg_path = "temp/user_bg.png"
            with open(bg_path, "wb") as f:
                f.write(uploaded_bg.getbuffer())
        else:
            st.warning("⚠️ 배경 이미지가 업로드되지 않아 기본 배경으로 진행합니다.")

        for idx, row in edited_df.iterrows():
            img_file = f"temp/frame_{idx}.png"
            audio_file = f"temp/voice_{idx}.mp3"
            
            create_overlay_card(bg_path, row["순위"], row["차종"], row["판매량"], row["대본"], img_file)
            asyncio.run(generate_tts(row["대본"], audio_file))
            
            audio_clip = AudioFileClip(audio_file)
            video_clip = ImageClip(img_file).set_duration(audio_clip.duration + 0.3).set_audio(audio_clip)
            clips.append(video_clip)
            
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "cardata_template_shorts.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        
        with open(output_file, "rb") as file:
            st.success("✨ 템플릿 기반 영상 제작 완료!")
            st.download_button(label="📥 최종 MP4 다운로드", data=file, file_name="cardata_final.mp4", mime="video/mp4")
