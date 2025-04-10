# -*- coding: utf-8 -*-
from PIL import Image
import os
import datetime
# import subprocess # GitHub Actions'da genellikle kullanılmaz
import re
import sys # Hata mesajları için

# --- Script Ayarları ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # Script'in bulunduğu dizin
# Repo kök dizinini script'in bulunduğu dizin olarak varsayıyoruz
# Eğer script'i repo içinde başka bir klasöre (örn: scripts/) koyarsanız,
# BASE_DIR = os.path.dirname(SCRIPT_DIR) gibi ayarlamanız gerekebilir.
BASE_DIR = SCRIPT_DIR
STATIC_DIR = os.path.join(BASE_DIR, "static")
# --- --- --- --- --- ---

# --- generate_site.py dosyasındaki klasorleri_Tara fonksiyonunu bulun ---

def klasorleri_Tara(ana_dizin):
    """Proje klasörlerini tarar ve proje bilgilerini toplar."""
    print(f"--- Klasör Taraması Başladı: {ana_dizin} ---")
    proje_listesi = []
    static_klasor_adi = os.path.basename(STATIC_DIR) # "static"
    # İşlenmesini istemediğiniz klasör adını buraya ekleyin
    repo_klasor_adi = "studiomoi.github.io" # Kendi repo adınızla veya loglarda görünen adla eşleştirin

    try:
        klasor_adlari = os.listdir(ana_dizin)
    except FileNotFoundError:
        print(f"HATA: Ana dizin bulunamadı: {ana_dizin}", file=sys.stderr)
        return []

    for klasor_adi in klasor_adlari:
        # ---- BU SATIRI GÜNCELLEYİN ----
        # Gizli klasörleri (.git, .github vb.), static klasörünü VE repo adını taşıyan klasörü atla
        if klasor_adi.startswith('.') or klasor_adi == static_klasor_adi or klasor_adi == repo_klasor_adi:
            print(f"  - Atlanıyor (Özel/Gizli/Repo): {klasor_adi}") # Bilgi mesajı (isteğe bağlı)
            continue # Döngünün başına dön, bu klasörü işleme
        # ---- GÜNCELLEME BİTTİ ----

        klasor_yolu = os.path.join(ana_dizin, klasor_adi)

        if os.path.isdir(klasor_yolu):
            print(f"-> Klasör Taranıyor: {klasor_adi}") # Bu mesaj artık repo klasörü için görünmemeli
            txt_dosyasi_adi = None
            try:
                dosya_adlari = os.listdir(klasor_yolu)
                for dosya_adi in dosya_adlari:
                    if dosya_adi.lower().endswith(".txt"):
                        txt_dosyasi_adi = dosya_adi
                        print(f"  - Bulunan .txt dosyası: {txt_dosyasi_adi}")
                        break
            except Exception as e:
                print(f"  - HATA: {klasor_adi} içindeki dosyalar okunurken hata: {e}", file=sys.stderr)
                continue

            if txt_dosyasi_adi:
                proje_bilgisi = {
                    "klasor_adi": klasor_adi,
                    "txt_dosyasi": txt_dosyasi_adi,
                }
                proje_listesi.append(proje_bilgisi)
            else:
                # Bu uyarı mesajı artık repo klasörü için görünmemeli
                print(f"  - UYARI: {klasor_adi} içinde .txt dosyası bulunamadı, geçiliyor.")

    print(f"--- Klasör Taraması Bitti: {len(proje_listesi)} proje bulundu ---")
    return proje_listesi

# --- Fonksiyonun geri kalanı ve script'in diğer kısımları aynı kalır ---

def index_html_Olustur(proje_bilgisi, ana_dizin, static_dizin):
    """Verilen proje için index.html dosyasını oluşturur."""
    klasor_adi = proje_bilgisi["klasor_adi"]
    txt_dosyasi_adi = proje_bilgisi["txt_dosyasi"]

    proje_klasor_yolu = os.path.join(ana_dizin, klasor_adi) # Artık ana_dizin'den başla
    txt_dosya_yolu = os.path.join(proje_klasor_yolu, txt_dosyasi_adi)
    index_html_yolu = os.path.join(proje_klasor_yolu, "index.html")

    print(f"-> '{klasor_adi}' için index.html oluşturuluyor...")

    # Gerekli şablonların yolları (static_dizin'e göre)
    gallery_template_path = os.path.join(static_dizin, "gallery.html")
    text_template_path = os.path.join(static_dizin, "text.html")
    image_template_path = os.path.join(static_dizin, "image.html")
    vimeo_template_path = os.path.join(static_dizin, "vimeo.html")
    youtube_template_path = os.path.join(static_dizin, "youtube.html")
    link_template_path = os.path.join(static_dizin, "link.html")
    project_template_path = os.path.join(static_dizin, "project.html")

    # Şablon varlık kontrolü
    for path in [gallery_template_path, text_template_path, image_template_path,
                 vimeo_template_path, youtube_template_path, link_template_path,
                 project_template_path]:
        if not os.path.isfile(path):
            print(f"  - HATA: Gerekli şablon bulunamadı: {path}", file=sys.stderr)
            return False

    html_icerik_parcalari = []
    galeri_resimleri = []
    paragraf_satirlari = []

    try:
        with open(txt_dosya_yolu, "r", encoding="utf-8") as f:
            satirlar = f.readlines()

        if not satirlar:
            print(f"  - UYARI: {txt_dosyasi_adi} dosyası boş.")
            return False

        proje_basligi = satirlar[0].strip()
        html_icerik_parcalari.append(f"<h1>{proje_basligi}</h1>")

        # --- .txt içeriğini işleme mantığı (öncekiyle aynı, sadece şablon yolları güncellendi) ---
        for satir_index, satir in enumerate(satirlar[1:]):
            satir = satir.strip()

            # Boş satır kontrolü ve birikenleri işleme
            if not satir:
                if galeri_resimleri:
                    with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                    img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                    html_icerik_parcalari.append(modul)
                    galeri_resimleri = []
                if paragraf_satirlari:
                    with open(text_template_path, "r", encoding="utf-8") as tf: paragraf_sablon = tf.read()
                    modul = paragraf_sablon.replace("{% block content %}{% endblock %}", " ".join(paragraf_satirlari))
                    html_icerik_parcalari.append(modul)
                    paragraf_satirlari = []
                continue

            # Görsel kontrolü
            parts = satir.split()
            image_names = [p for p in parts if p.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]

            if len(image_names) > 1: # Galeri
                if galeri_resimleri: # Önceki birikeni kapat
                    with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                    img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                    html_icerik_parcalari.append(modul)
                    galeri_resimleri = []
                with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                img_tags = [f'<img src="{img}" alt="Proje Galeri Resmi">' for img in image_names]
                modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                html_icerik_parcalari.append(modul)
                continue
            elif len(image_names) == 1: # Tek resim
                if galeri_resimleri: # Önceki birikeni kapat
                    with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                    img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                    html_icerik_parcalari.append(modul)
                    galeri_resimleri = []
                with open(image_template_path, "r", encoding="utf-8") as tf: resim_sablon = tf.read()
                modul = resim_sablon.replace("{% block resim_url %}{% endblock %}", image_names[0])
                html_icerik_parcalari.append(modul)
                continue

            # Video kontrolü (Youtube/Vimeo ID çıkarma iyileştirildi)
            video_url = satir
            video_id = None
            video_template = None
            satir_lower = satir.lower()

            if "vimeo.com" in satir_lower:
                match = re.search(r"vimeo\.com/(\d+)", video_url)
                if match:
                    video_id = match.group(1)
                    video_template = vimeo_template_path
            # youtu.be/ ile biten veya v= içeren URL'ler
            elif ("youtu.be/" in satir_lower or "googleusercontent.com/youtube.com/" in satir_lower):
                match_param = re.search(r"[?&]v=([^&]+)", video_url)
                match_path = re.search(r"youtu.be//([^/?]+)", video_url)
                match_be = re.search(r"googleusercontent.com/youtube.com//([^/?]+)", video_url)
                if match_param:
                    video_id = match_param.group(1)
                elif match_path:
                    video_id = match_path.group(1)
                elif match_be:
                     video_id = match_be.group(1)

                if video_id:
                     video_template = youtube_template_path


            if video_id and video_template:
                 if galeri_resimleri: # Önceki birikeni kapat
                    with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                    img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                    html_icerik_parcalari.append(modul)
                    galeri_resimleri = []
                 with open(video_template, "r", encoding="utf-8") as tf: video_sablon = tf.read()
                 modul = video_sablon.replace("{% block video_id %}{% endblock %}", video_id)
                 html_icerik_parcalari.append(modul)
                 continue

            # Link kontrolü (URL'nin başta, sonda veya tek başına olması durumu)
            link_url = None
            link_metni = None
            # Önce "Metin URL" veya "URL Metin" formatını ara
            link_eslesme_metin_url = re.search(r"^(.*?)\s+(https?://\S+)$", satir)
            link_eslesme_url_metin = re.search(r"^(https?://\S+)\s+(.*)$", satir)
            # Sadece URL var mı?
            link_eslesme_sadece_url = re.search(r"^(https?://\S+)$", satir)

            if link_eslesme_metin_url:
                link_metni = link_eslesme_metin_url.group(1).strip()
                link_url = link_eslesme_metin_url.group(2).strip()
            elif link_eslesme_url_metin:
                link_url = link_eslesme_url_metin.group(1).strip()
                link_metni = link_eslesme_url_metin.group(2).strip()
            elif link_eslesme_sadece_url:
                link_url = link_eslesme_sadece_url.group(1).strip()
                link_metni = link_url # Metin olarak da URL'yi kullan

            if link_url and link_metni:
                if galeri_resimleri: # Önceki birikeni kapat
                    with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                    img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                    html_icerik_parcalari.append(modul)
                    galeri_resimleri = []
                with open(link_template_path, "r", encoding="utf-8") as tf: link_sablon = tf.read()
                # Template'de yer tutucuların aynı olduğundan emin olun: {% block link_url %} ve {% block link_metni %}
                modul = link_sablon.replace("{% block link_url %}", link_url)
                modul = modul.replace("{% block link_metni %}", link_metni)
                html_icerik_parcalari.append(modul)
                continue

            # Yukarıdakilerin hiçbiri değilse, metin satırıdır
            else:
                paragraf_satirlari.append(satir)
                # Cümle sonu kontrolüyle paragrafı kapat (opsiyonel)
                if satir.endswith(('.', '!', '?')):
                    if galeri_resimleri: # Önceki birikeni kapat
                        with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
                        img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                        modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
                        html_icerik_parcalari.append(modul)
                        galeri_resimleri = []
                    with open(text_template_path, "r", encoding="utf-8") as tf: paragraf_sablon = tf.read()
                    modul = paragraf_sablon.replace("{% block content %}{% endblock %}", " ".join(paragraf_satirlari))
                    html_icerik_parcalari.append(modul)
                    paragraf_satirlari = []

        # Döngü sonrasında kalanları işle
        if galeri_resimleri:
            with open(gallery_template_path, "r", encoding="utf-8") as tf: galeri_sablon = tf.read()
            img_tags = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
            modul = galeri_sablon.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(img_tags))
            html_icerik_parcalari.append(modul)
        if paragraf_satirlari:
            with open(text_template_path, "r", encoding="utf-8") as tf: paragraf_sablon = tf.read()
            modul = paragraf_sablon.replace("{% block content %}{% endblock %}", " ".join(paragraf_satirlari))
            html_icerik_parcalari.append(modul)

        # Ana proje şablonunu oku ve içeriği yerleştir
        with open(project_template_path, "r", encoding="utf-8") as tf:
            proje_sablon = tf.read()

        html_icerik = proje_sablon.replace("{% block proje_icerigi %}{% endblock %}", "\n".join(html_icerik_parcalari))
        html_icerik = html_icerik.replace("{% block title %}{% endblock %}", proje_basligi)

        # Sonuç HTML dosyasını yaz
        with open(index_html_yolu, "w", encoding="utf-8") as f:
            f.write(html_icerik)
        print(f"  - Başarılı: '{index_html_yolu}' oluşturuldu.")
        return True

    except FileNotFoundError:
        print(f"  - HATA: {txt_dosya_yolu} okunamadı.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  - HATA: '{klasor_adi}' için index.html oluşturulurken beklenmedik hata: {e}", file=sys.stderr)
        return False


def ana_sayfayi_Guncelle(proje_listesi, ana_dizin, static_dizin):
    """Ana index.html sayfasını günceller."""
    print(f"--- Ana Sayfa Güncellemesi Başladı: {ana_dizin} ---")
    proje_listesi_html_satirlari = []
    ana_sayfa_sablon_yolu = os.path.join(static_dizin, "index.html") # Ana sayfa için static'teki index.html şablonu
    ana_sayfa_cikti_yolu = os.path.join(ana_dizin, "index.html")    # Çıktı repo köküne yazılacak

    if not os.path.isfile(ana_sayfa_sablon_yolu):
         print(f"  - HATA: Ana sayfa şablonu bulunamadı: {ana_sayfa_sablon_yolu}", file=sys.stderr)
         return False

    def txt_dosyasi_numarasini_al(proje_bilgisi):
        txt_dosyasi_adi = proje_bilgisi["txt_dosyasi"]
        numaralar = re.findall(r'\d+', txt_dosyasi_adi)
        # Numara bulunamazsa sıralama için büyük bir değer verilebilir veya 0
        return int(numaralar[0]) if numaralar else 9999

    try:
        # Projeleri .txt dosyasındaki numaraya göre sırala
        sirali_proje_listesi = sorted(proje_listesi, key=txt_dosyasi_numarasini_al)
    except Exception as e:
        print(f"  - UYARI: Projeler sıralanamadı ({e}), varsayılan sıra kullanılacak.")
        sirali_proje_listesi = proje_listesi

    for proje_bilgisi in sirali_proje_listesi:
        klasor_adi = proje_bilgisi["klasor_adi"]
        txt_dosyasi_adi = proje_bilgisi["txt_dosyasi"]
        proje_klasor_yolu = os.path.join(ana_dizin, klasor_adi) # Ana dizine göre
        txt_dosya_yolu = os.path.join(proje_klasor_yolu, txt_dosyasi_adi)

        thumbnail_dosya_adi = None
        thumbnail_url_rel = None # HTML içindeki göreceli yol
        genislik, yukseklik = 0, 0 # Başlangıç değerleri
        proje_basligi = klasor_adi # Başlık bulunamazsa klasör adını kullan

        try:
            # Başlığı .txt dosyasından oku
            with open(txt_dosya_yolu, "r", encoding="utf-8") as f:
                proje_basligi = f.readline().strip() or klasor_adi

            # Thumbnail bul ve boyutlarını al
            for dosya_adi in os.listdir(proje_klasor_yolu):
                dosya_lower = dosya_adi.lower()
                if dosya_lower.startswith("thumbnail.") and dosya_lower.endswith((".jpg", ".jpeg", ".gif", ".png")):
                    thumbnail_dosya_adi = dosya_adi
                    thumbnail_dosya_yolu_abs = os.path.join(proje_klasor_yolu, thumbnail_dosya_adi)
                    thumbnail_url_rel = f"{klasor_adi}/{thumbnail_dosya_adi}" # Göreceli yol
                    try:
                        with Image.open(thumbnail_dosya_yolu_abs) as img:
                            genislik, yukseklik = img.size
                        print(f"  - Thumbnail bulundu: {klasor_adi}/{thumbnail_dosya_adi} ({genislik}x{yukseklik})")
                        break # İlk bulunanı al
                    except Exception as img_err:
                        print(f"  - UYARI: Thumbnail dosyası okunamadı/boyut alınamadı: {thumbnail_url_rel} ({img_err})")
                        genislik, yukseklik = 0, 0 # Boyutları sıfırla
                        break # Yine de bulduk, devam et

        except FileNotFoundError:
             print(f"  - UYARI: {klasor_adi} için .txt dosyası okunamadı ({txt_dosya_yolu}), başlık olarak klasör adı kullanılacak.")
        except Exception as e:
             print(f"  - UYARI: {klasor_adi} işlenirken hata: {e}")
             continue # Bu projeyi atla

        if thumbnail_url_rel: # Thumbnail bulunduysa ekle
            proje_linki = f"{klasor_adi}/" # Klasördeki index.html'e link (sonuna / eklemek iyi olabilir)
            # Width ve height eklenmiş brick HTML'i
            width_attr = f'width="{genislik}"' if genislik > 0 else ""
            height_attr = f'height="{yukseklik}"' if yukseklik > 0 else ""
            proje_listesi_html_satiri = f'<div class="brick"><a href="{proje_linki}"><img src="{thumbnail_url_rel}" alt="{proje_basligi}" {width_attr} {height_attr}></a></div>'
            proje_listesi_html_satirlari.append(proje_listesi_html_satiri)
        else:
            print(f"  - UYARI: {klasor_adi} için thumbnail bulunamadı, ana sayfaya eklenmiyor.")

    # Ana sayfa şablonunu oku
    try:
        with open(ana_sayfa_sablon_yolu, "r", encoding="utf-8") as sablon_dosyasi:
            ana_sayfa_sablon_icerigi = sablon_dosyasi.read()
    except Exception as e:
         print(f"  - HATA: Ana sayfa şablonu okunamadı: {ana_sayfa_sablon_yolu} ({e})", file=sys.stderr)
         return False

    # Şablonu proje listesiyle birleştir
    ana_sayfa_html_icerigi = ana_sayfa_sablon_icerigi.replace("{% block proje_listesi_icerigi %}{% endblock %}", "\n".join(proje_listesi_html_satirlari))

    # Sonuç ana sayfa HTML'ini yaz
    try:
        with open(ana_sayfa_cikti_yolu, "w", encoding="utf-8") as f:
            f.write(ana_sayfa_html_icerigi)
        print(f"--- Ana Sayfa Güncellemesi Bitti: '{ana_sayfa_cikti_yolu}' güncellendi ---")
        return True
    except Exception as e:
        print(f"  - HATA: Ana sayfa ({ana_sayfa_cikti_yolu}) yazılırken hata: {e}", file=sys.stderr)
        return False

def ana_dongu(base_dir, static_dir):
    """Ana iş akışı: Tara, oluştur, güncelle."""
    print("===== WEBSITE GENERATION STARTED =====")
    start_time = datetime.datetime.now()

    # Adım 1: Proje klasörlerini tara (repo kök dizininden başla)
    proje_listesi = klasorleri_Tara(base_dir)

    if not proje_listesi:
        print("Hiç proje bulunamadı veya taranırken hata oluştu. İşlem durduruluyor.")
        return

    # Adım 2: Her proje için index.html oluştur
    print("\n--- Proje Sayfaları Oluşturuluyor ---")
    basarili_projeler = []
    for proje_bilgisi in proje_listesi:
        if index_html_Olustur(proje_bilgisi, base_dir, static_dir):
             basarili_projeler.append(proje_bilgisi) # Sadece başarılı olanları ana sayfaya ekle
    print("--- Proje Sayfaları Oluşturma Bitti ---")


    # Adım 3: Ana index.html sayfasını güncelle (sadece başarılı oluşturulan projelerle)
    if basarili_projeler:
         print("\n--- Ana Sayfa Güncelleniyor ---")
         ana_sayfayi_Guncelle(basarili_projeler, base_dir, static_dir)
         print("--- Ana Sayfa Güncelleme Bitti ---")
    else:
         print("\nHiçbir proje sayfası başarıyla oluşturulamadığı için ana sayfa güncellenmedi.")


    end_time = datetime.datetime.now()
    gecen_sure = end_time - start_time
    print(f"\n===== WEBSITE GENERATION FINISHED (Duration: {gecen_sure}) =====")

if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında BASE_DIR ve STATIC_DIR kullanılır
    if not os.path.isdir(STATIC_DIR):
        print(f"HATA: Static klasörü bulunamadı: {STATIC_DIR}", file=sys.stderr)
        print("Lütfen script'in ve 'static' klasörünün doğru yerde olduğundan emin olun.")
    else:
        ana_dongu(BASE_DIR, STATIC_DIR)