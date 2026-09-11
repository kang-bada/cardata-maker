import streamlit as st
import os
import asyncio
import urllib.request
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

st.set_page_config(page_title="컨텐츠 제작소 - 카데이터 숏폼", page_icon="🚗")
st.title("🚗 컨텐츠 제작소: 숏폼 자동화 팩토리")
st.write("매월 판매량 데이터와 대본만 갱신하세요. 우리 채널만의 고정된 시그니처 디자인으로 풀영상이 자동 완성됩니다.")

# 폰트 세팅 (고딕체 고정)
font_path = "NanumGothic.ttf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf", font_path)

# 1. 사용자 입력 UI (매월 데이터 갱신용)
st.subheader("📊 이번 달 데이터 입력")
st.write("아래 표의 빈칸을 클릭해 이번 달의 순위, 차종, 판매량, 대본을 수정해 주세요.")

# 스트림릿 웹 화면에서 직접 수정할 수 있는 데이터 표
default_data = pd.DataFrame(
    [
        {"순위": "5위", "차종": "기아 스포티지", "판매량": 3874, "대본": "5위는 3,874대로 기아 스포티지입니다."},
        {"순위": "4위", "차종": "기아 카니발", "판매량": 4186, "대본": "4위는 4,186대로 아빠들의 로망, 기아 카니발이 차지했습니다."},
        {"순위": "3위", "차종": "현대 더 뉴 그랜저", "판매량": 5931, "대본": "3위는 5,931대로 현대 더 뉴 그랜저가 세단의 자존심을 지켰습니다."},
        {"순위": "2위", "차종": "기아 쏘렌토", "판매량": 6397, "대본": "2위는 6,397대로 굳건한 1위 패밀리 SUV, 기아 쏘렌토입니다."},
        {"순위": "1위", "차종": "테슬라 Model Y", "판매량": 9638, "대본": "대망의 1위는 무려 9,638대, 테슬라 모델 Y입니다! 압도적 1위네요."}
    ]
)

# 표를 화면에 띄우고 사용자가 수정한 값을 edited_df로 받음
edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

# 2. 영상 생성 엔진 (고정된 템플릿 포맷)
async def generate_tts(text, path):
    communicate = edge_tts.Communicate(text, "ko-KR-InJoonNeural")
    await communicate.save(path)

def create_card(rank, title, count, script, max_count, path):
    # 우리 채널만의 고정 다크 배경 (1080x1920)
    img = Image.new("RGB", (1080, 1920), color=(15, 18, 26))
    draw = ImageDraw.Draw(img)
    
    font_title = ImageFont.truetype(font_path, 90)
    font_rank = ImageFont.truetype(font_path, 50)
    font_num = ImageFont.truetype(font_path, 75)
    font_script = ImageFont.truetype(font_path, 40)
    
    # 상단 고정 헤더 (채널 정체성)
    draw.text((540, 200), "CARDATA MONTHLY REPORT", font=font_rank, fill=(100, 150, 200), anchor="mm")
    
    # 메인 인포그래픽 카드 배경
    draw.rounded_rectangle([100, 320, 980, 1350], radius=40, fill=(22, 28, 41), outline=(45, 55, 75), width=3)
    
    # 순위 배지 (1위는 빨간색, 나머지는 파란색으로 자동 변경)
    rank_color = (255, 75, 75) if rank == "1위" else (0, 210, 255)
    draw.rounded_rectangle([180, 400, 340, 490], radius=15, fill=rank_color)
    draw.text((260, 445), str(rank), font=font_rank, fill=(255, 255, 255), anchor="mm")
    
    # 데이터 타이포그래피
    draw.text((180, 560), str(title), font=font_title, fill=(255, 255, 255))
    draw.text((180, 800), "월간 판매량", font=font_script, fill=(120, 140, 170))
    draw.text((180, 880), f"{int(count):,} 대", font=font_num, fill=rank_color)
    
    # 판매량 비례 게이지 바 (막대그래프) 자동 생성
    draw.rounded_rectangle([180, 1020, 900, 1060], radius=20, fill=(35, 45, 65))
    fill_width = 180 + int((count / max_count) * (900 - 180))
    draw.rounded_rectangle([180, 1020, fill_width, 1060], radius=20, fill=rank_color)
    
    # 하단 자막 영역 고정
    draw.rounded_rectangle([100, 1500, 980, 1750], radius=30, fill=(24, 30, 44))
    
    # 자막 자동 줄바꿈
    if len(str(script)) > 26:
        line1 = str(script)[:26]
        line2 = str(script)[26:]
        draw.text((540, 1600), line1, font=font_script, fill=(240, 245, 255), anchor="mm")
        draw.text((540, 1660), line2, font=font_script, fill=(240, 245, 255), anchor="mm")
    else:
        draw.text((540, 1625), str(script), font=font_script, fill=(240, 245, 255), anchor="mm")

    img.save(path)

# 3. 렌더링 실행 버튼
if st.button("🎬 우리 채널 숏폼 풀영상 렌더링 시작"):
    with st.spinner("데이터를 분석하여 5위부터 1위까지 풀영상을 조립하고 있습니다... (약 30~50초 소요)"):
        os.makedirs("temp", exist_ok=True)
        clips = []
        max_sales = edited_df["판매량"].max() # 1위 판매량을 기준으로 게이지 바 비율 계산
        
        for idx, row in edited_df.iterrows():
            img_file = f"temp/frame_{idx}.png"
            audio_file = f"temp/voice_{idx}.mp3"
            
            # 우리만의 포맷으로 이미지와 음성 찍어내기
            create_card(row["순위"], row["차종"], row["판매량"], row["대본"], max_sales, img_file)
            asyncio.run(generate_tts(row["대본"], audio_file))
            
            # 클립 생성 후 리스트에 추가
            audio_clip = AudioFileClip(audio_file)
            video_clip = ImageClip(img_file).set_duration(audio_clip.duration + 0.3).set_audio(audio_clip)
            clips.append(video_clip)
            
        # 조각난 5~1위 영상을 하나로 이어붙이기
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "cardata_monthly_shorts.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        
        with open(output_file, "rb") as file:
            st.success("✅ 우리 채널 고정 포맷 영상 제작 완료!")
            st.download_button(label="📥 완성된 MP4 다운로드", data=file, file_name="cardata_monthly.mp4", mime="video/mp4")
