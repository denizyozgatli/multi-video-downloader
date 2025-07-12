import streamlit as st
import yt_dlp
import os
import re
import time

# --- Sayfa Ayarları ve Başlık ---
st.set_page_config(
    page_title="Sosyal Medya Video İndirici",
    page_icon="📥",
    layout="centered"
)

st.title("📥 Sosyal Medya Video İndirici")
st.markdown("TikTok, Twitter ve Instagram'dan videoları kolayca indirin. Sadece videonun linkini yapıştırın!")

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
        # Hata durumunda rastgele bir isim kullan
        return os.path.join(DOWNLOAD_DIR, f"video_{int(time.time())}.mp4")


def download_video_streamlit(url, placeholder):
    """Streamlit arayüzü için video indirme fonksiyonu."""
    
    file_path = get_video_info(url)
    
    ydl_opts = {
        'outtmpl': file_path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        # İlerleme durumunu yakalamak için hook
        'progress_hooks': [lambda d: placeholder.text(f"İndiriliyor... {d.get('_percent_str', '0%')}")]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return file_path
    except Exception as e:
        st.error(f"Hata: Video indirilemedi. URL'nin doğru ve herkese açık olduğundan emin olun.")
        st.error(f"Detay: {e}")
        return None

# --- Arayüz Elemanları ---
url = st.text_input("🔗 Video URL'sini buraya yapıştırın:", placeholder="https.tiktok.com/...")

if st.button("📥 Videoyu İndir"):
    if url:
        # URL'nin temel bir geçerlilik kontrolü
        if "tiktok.com" in url or "twitter.com" in url or "instagram.com" in url or "x.com" in url:
            progress_placeholder = st.empty()
            with st.spinner("Video bilgileri alınıyor..."):
                video_path = download_video_streamlit(url, progress_placeholder)
            
            if video_path and os.path.exists(video_path):
                st.success("✅ Video başarıyla indirildi!")
                
                # Videoyu doğrudan sayfada göster
                st.video(video_path)
                
                # İndirme butonu
                with open(video_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Bilgisayarına Kaydet",
                        data=file,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4"
                    )
                
                # Sunucudaki dosyayı temizlemek için (isteğe bağlı ama iyi bir pratik)
                # os.remove(video_path) 
                # Not: Streamlit Cloud'da geçici dosya sistemi kullanılır, 
                # bu nedenle manuel silme her zaman gerekli olmayabilir.
        else:
            st.warning("Lütfen geçerli bir TikTok, Twitter veya Instagram URL'si girin.")
    else:
        st.warning("Lütfen bir URL girin.")