import streamlit as st
import os
import asyncio
import urllib.request
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

st.set_page_config(page_title="컨텐츠 제작소 - 카데이터 숏폼", page_icon="🚗")
st.title("🚗 컨텐츠 제작소: 프리미엄 숏폼 팩토리")
st.write("디자인 퀄리티가 대폭 업그레이드된 프로급 다크 테마 인포그래픽 포맷입니다.")

# 고품질 폰트 세팅
font_path = "NanumGothic.ttf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf", font_path)

# 기본 데이터 세팅
default_data = pd.DataFrame(
    [
        {"순위": "5위", "차종": "기아 스포티지", "판매량": 3874, "대본": "5위는 3,874대로 기아 스포티지입니다."},
        {"순위": "4위", "차종": "기아 카니발", "판매량": 4186, "대본": "4위는 4,186대로 아빠들의 로망, 기아 카니발이 차지했습니다."},
        {"순위": "3위", "차종": "현대 더 뉴 그랜저", "판매량": 5931, "대본": "3위는 5,931대로 현대 더 뉴 그랜저가 세단의 자존심을 지켰습니다."},
        {"순위": "2위", "차종": "기아 쏘렌토", "판매량": 6397, "대본": "2위는 6,397대로 굳건한 1위 패밀리 SUV, 기아 쏘렌토입니다."},
        {"순위": "1위", "차종": "테슬라 Model Y", "판매량": 9638, "대본": "대망의 1위는 무려 9,638대, 테슬라 모델 Y입니다! 압도적 1위네요."}
    ]
)

edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

async def generate_tts(text, path):
    communicate = edge_tts.Communicate(text, "ko-KR-InJoonNeural")
    await communicate.save(path)

def create_premium_card(rank, title, count, script, max_count, path):
    width, height = 1080, 1920
    # 1) 고급스러운 다크 네이비/그레이 톤 그라데이션 베이스 배경
    img = Image.new("RGB", (width, height), color=(10, 13, 20))
    draw = ImageDraw.Draw(img)
    
    # 폰트 사이즈 정의
    font_header = ImageFont.truetype(font_path, 42)
    font_rank = ImageFont.truetype(font_path, 55)
    font_title = ImageFont.truetype(font_path, 80)
    font_num_label = ImageFont.truetype(font_path, 38)
    font_num = ImageFont.truetype(font_path, 85)
    font_script = ImageFont.truetype(font_path, 44)
    
    # 2) 상단 브랜드 로고 및 채널 헤더 배지
    draw.rounded_rectangle([140, 160, 940, 250], radius=25, fill=(18, 24, 38), outline=(35, 48, 75), width=2)
    draw.text((width // 2, 205), "⚡ CAR DATA RANKING BRIEFING", font=font_header, fill=(0, 220, 255), anchor="mm")
    
    # 3) 메인 인포그래픽 글래스모피즘 카드 박스
    card_box = [80, 320, 1000, 1400]
    draw.rounded_rectangle(card_box, radius=45, fill=(18, 24, 38), outline=(45, 60, 90), width=3)
    
    # 순위별 컬러 포인트 (1위: 강렬한 네온 레드/코랄, 그 외: 시안 블루)
    is_first = (rank == "1위")
    accent_color = (255, 65, 95) if is_first else (0, 210, 255)
    sub_bg_color = (45, 20, 30) if is_first else (15, 45, 60)
    
    # 순위 배지 (입체 효과)
    draw.rounded_rectangle([140, 390, 320, 490], radius=20, fill=sub_bg_color, outline=accent_color, width=2)
    draw.text((230, 440), str(rank), font=font_rank, fill=accent_color, anchor="mm")
    
    # 차종 이름 (줄바꿈 고려)
    draw.text((140, 560), str(title), font=font_title, fill=(255, 255, 255))
    
    # 구분선 추가
    draw.line([140, 710, 940, 710], fill=(35, 48, 75), width=2)
    
    # 판매량 통계 수치 강조 영역
    draw.text((140, 760), "MONTHLY SALES VOLUME", font=font_num_label, fill=(120, 145, 180))
    draw.text((140, 850), f"{int(count):,} 대", font=font_num, fill=accent_color)
    
    # 4) 세련된 게이지 바 (막대그래프)
    bar_bg = [140, 1040, 940, 1100]
    draw.rounded_rectangle(bar_bg, radius=30, fill=(25, 34, 50))
    
    fill_width = 140 + int((count / max_count) * (940 - 140))
    if fill_width > 140:
        draw.rounded_rectangle([140, 1040, max(fill_width, 200), 1100], radius=30, fill=accent_color)
    
    # 5) 하단 자막 영역 (가독성을 극대화한 모던 박스)
    sub_box = [80, 1500, 1000, 1760]
    draw.rounded_rectangle(sub_box, radius=35, fill=(14, 19, 30), outline=(35, 48, 75), width=2)
    
    # 자막 텍스트 자동 정돈
    script_str = str(script)
    if len(script_str) > 24:
        mid_idx = len(script_str) // 2
        space_idx = script_str.find(' ', mid_idx - 4, mid_idx + 6)
        if space_idx == -1: space_idx = mid_idx
        line1 = script_str[:space_idx].strip()
        line2 = script_str[space_idx:].strip()
        draw.text((width // 2, 1595), line1, font=font_script, fill=(245, 248, 255), anchor="mm")
        draw.text((width // 2, 1665), line2, font=font_script, fill=(245, 248, 255), anchor="mm")
    else:
        draw.text((width // 2, 1630), script_str, font=font_script, fill=(245, 248, 255), anchor="mm")

    img.save(path)

if st.button("🎬 프리미엄 숏폼 풀영상 렌더링 시작"):
    with st.spinner("프로급 인포그래픽 디자인과 고음질 음성을 렌더링 중입니다..."):
        os.makedirs("temp", exist_ok=True)
        clips = []
        max_sales = edited_df["판매량"].max()
        
        for idx, row in edited_df.iterrows():
            img_file = f"temp/frame_{idx}.png"
            audio_file = f"temp/voice_{idx}.mp3"
            
            create_premium_card(row["순위"], row["차종"], row["판매량"], row["대본"], max_sales, img_file)
            asyncio.run(generate_tts(row["대본"], audio_file))
            
            audio_clip = AudioFileClip(audio_file)
            video_clip = ImageClip(img_file).set_duration(audio_clip.duration + 0.3).set_audio(audio_clip)
            clips.append(video_clip)
            
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "cardata_premium_shorts.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        
        with open(output_file, "rb") as file:
            st.success("✨ 프리미엄 영상 제작 완료!")
            st.download_button(label="📥 고화질 MP4 다운로드", data=file, file_name="cardata_premium.mp4", mime="video/mp4")
