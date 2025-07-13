import streamlit as st
import yt_dlp
import os
import re
import time

# --- Sayfa Ayarları ve Başlık ---
st.set_page_config(
    page_title="Video Downloader",
    page_icon="📥",
    layout="centered"
)

st.title("Video Downloader")
st.markdown("Easily download videos from TikTok, Twitter and Instagram!")

# --- İndirme Klasörü ---
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def sanitize_filename(filename):
    """Dosya adlarındaki geçersiz karakterleri temizler."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_video_info(url):
    """yt-dlp kullanarak video bilgilerini (başlık ve dosya yolu) alır."""
    try:
        ydl_opts = {'quiet': True, 'noplaylist': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = sanitize_filename(info_dict.get('title', 'video'))
            ext = info_dict.get('ext', 'mp4')
            filename = f"{title}.{ext}"
            return os.path.join(DOWNLOAD_DIR, filename)
    except Exception:
        return os.path.join(DOWNLOAD_DIR, f"video_{int(time.time())}.mp4")


def download_video_streamlit(url, placeholder):
    """Streamlit arayüzü için video indirme fonksiyonu."""
    
    file_path = get_video_info(url)
    
    ydl_opts = {
        'outtmpl': file_path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [lambda d: placeholder.text(f"Downloading... {d.get('_percent_str', '0%')}")]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return file_path
    except Exception as e:
        st.error(f"Error: The video could not be downloaded. Make sure the URL is correct and public.")
        st.error(f"Detay: {e}")
        return None

url = st.text_input("Paste video URL here:", placeholder="https.tiktok.com/...")

if st.button("Download"):
    if url:
        if "tiktok.com" in url or "twitter.com" in url or "instagram.com" in url or "x.com" in url:
            progress_placeholder = st.empty()
            with st.spinner("Retrieving video information......"):
                video_path = download_video_streamlit(url, progress_placeholder)
            
            if video_path and os.path.exists(video_path):
                st.success("Video downloaded successfully!")
                
                st.video(video_path)
                
                with open(video_path, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4"
                    )
                    
        else:
            st.warning("Please enter a valid URL.")
    else:
        st.warning("Please enter a URL.")

# --- FOOTER ---
st.markdown(
    """
    <div style="text-align: center; color: grey;">
        <p>
            Made with ❤️ by 
            <a 
                href="https://github.com/denizyozgatli" 
                target="_blank" 
                style="color: #FF4B4B; text-decoration: none;"
            >
                denizyozgatli
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
