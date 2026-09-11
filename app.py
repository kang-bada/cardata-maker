import streamlit as st
import os
import asyncio
import urllib.request
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageClip

st.set_page_config(page_title="카데이터 숏폼 제작소", page_icon="🚗")
st.title("🚗 카데이터 숏폼 자동 제작소")
st.write("버튼 한 번으로 데이터 대본을 MP4 영상으로 자동 렌더링합니다.")

# 스트림릿 클라우드용 한글 폰트 자동 다운로드
font_path = "NanumGothic.ttf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf", font_path)

# 임시 데이터
DATA = [
    {"rank": "1위", "title": "테슬라 Model Y", "script": "대망의 1위는 테슬라 모델 Y입니다! 압도적인 1위네요."}
]

async def generate_tts(text, path):
    communicate = edge_tts.Communicate(text, "ko-KR-InJoonNeural")
    await communicate.save(path)

def create_image(item, path):
    img = Image.new("RGB", (1080, 1920), color=(15, 18, 26))
    draw = ImageDraw.Draw(img)
    font_bold = ImageFont.truetype(font_path, 90)
    font_mid = ImageFont.truetype(font_path, 50)
    
    draw.text((540, 800), item["rank"], font=font_mid, fill=(0, 210, 255), anchor="mm")
    draw.text((540, 960), item["title"], font=font_bold, fill=(255, 255, 255), anchor="mm")
    img.save(path)

if st.button("🎬 숏폼 영상 만들기 (테스트)"):
    with st.spinner("서버에서 AI 음성 생성 및 영상을 렌더링 중입니다... (약 10초 소요)"):
        os.makedirs("temp", exist_ok=True)
        img_file = "temp/frame.png"
        audio_file = "temp/voice.mp3"
        output_file = "cardata_test.mp4"

        create_image(DATA[0], img_file)
        asyncio.run(generate_tts(DATA[0]["script"], audio_file))

        audio_clip = AudioFileClip(audio_file)
        video_clip = ImageClip(img_file).set_duration(audio_clip.duration + 0.5).set_audio(audio_clip)
        video_clip.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")

        with open(output_file, "rb") as file:
            st.success("✅ 영상 제작 완료!")
            st.download_button(label="📥 MP4 다운로드", data=file, file_name="cardata_shorts.mp4", mime="video/mp4")
