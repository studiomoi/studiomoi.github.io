# -*- coding: utf-8 -*-
from PIL import Image
import os
import datetime
import subprocess
import re # Regular expression kütüphanesi URL tespiti için (ileride kullanacağız)

def klasorleri_Tara(ana_dizin):
    """Proje klasörlerini tarar ve proje bilgilerini toplar (.txt dosyası kontrolü eklendi)."""
    proje_listesi = [] # Proje bilgilerini saklayacağımız liste

    klasor_adlari = os.listdir(ana_dizin) # Ana dizindeki tüm dosya ve klasörlerin listesini al

    for klasor_adi in klasor_adlari: # Klasör adlarını tek tek döngüye al
        klasor_yolu = os.path.join(ana_dizin, klasor_adi) # Klasörün tam yolunu oluştur

        if klasor_adi == "static": # static klasörünü atla
            continue # Döngünün başına dön, static klasörünü işleme

        if os.path.isdir(klasor_yolu): # Eğer bir klasör ise (dosya değilse)
            print(f"{klasor_adi}") # Konsola bilgi yazdır (isteğe bağlı)

            txt_dosyasi_adi = None # txt dosyası adını tutacak değişken

            dosya_adlari = os.listdir(klasor_yolu) # Proje klasöründeki dosyaların listesini al
            for dosya_adi in dosya_adlari: # Proje klasöründeki dosyaları döngüye al
                if dosya_adi.endswith(".txt"): # Eğer dosya adı .txt ile bitiyorsa
                    txt_dosyasi_adi = dosya_adi # txt dosyası adını değişkene kaydet
                    break # İlk .txt dosyasını bulduktan sonra döngüden çık (her klasörde bir tane .txt dosyası bekliyoruz)

            if txt_dosyasi_adi: # YENİ KOD: Eğer txt dosyası bulunduysa
                proje_bilgisi = { # Sadeleştirilmiş proje bilgileri sözlüğü
                    "klasor_adi": klasor_adi, # Klasör adı
                    "txt_dosyasi": txt_dosyasi_adi, # txt dosyası adı
                }
                proje_listesi.append(proje_bilgisi) # Proje bilgilerini listeye ekle
            else: # YENİ KOD: Eğer txt dosyası bulunamadıysa
                print(f"{klasor_adi} projesinin txt dosyası yok onu geçiyorum.") # Konsola uyarı mesajı yazdır (isteğe bağlı)

        # else bloğu kaldırıldı, klasör olmayan dosyalar için herhangi bir işlem yapmıyoruz

    return proje_listesi # Proje listesini geri döndür

def index_html_Olustur(proje_bilgisi):
    klasor_adi = proje_bilgisi["klasor_adi"]
    txt_dosyasi_adi = proje_bilgisi["txt_dosyasi"]

    proje_klasor_yolu = os.path.join("..", klasor_adi)
    txt_dosya_yolu = os.path.join(proje_klasor_yolu, txt_dosyasi_adi)
    index_html_yolu = os.path.join(proje_klasor_yolu, "index.html")

    html_icerik_parcalari = []
    galeri_resimleri = []  # Birkaç satırdan gelen resimleri toplamak için
    paragraf_satirlari = []

    with open(txt_dosya_yolu, "r", encoding="utf-8") as f:
        satirlar = f.readlines()

        proje_basligi = satirlar[0].strip()
        html_icerik_parcalari.append(f"<h1>{proje_basligi}</h1>")

        for satir in satirlar[1:]:
            satir = satir.strip()
            # Boş satır geldiğinde, varsa biriken galeri veya paragrafı finalize et
            if not satir:
                if galeri_resimleri:
                    with open(os.path.join("../static", "gallery.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        galeri_sablon_icerigi = sablon_dosyasi.read()
                    galeri_resim_html_listesi = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    galeri_modul_icerigi = galeri_sablon_icerigi.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(galeri_resim_html_listesi))
                    html_icerik_parcalari.append(galeri_modul_icerigi)
                    galeri_resimleri = []
                if paragraf_satirlari:
                    with open(os.path.join("../static", "text.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        paragraf_sablon_icerigi = sablon_dosyasi.read()
                    paragraf_modul_icerigi = paragraf_sablon_icerigi.replace("{% block content %}{% endblock %}", " ".join(paragraf_satirlari))
                    html_icerik_parcalari.append(paragraf_modul_icerigi)
                    paragraf_satirlari = []
                continue

            # Tek satır içinde birden fazla görsel adı varsa (boşluklarla ayrılmış)
            parts = satir.split()
            image_names = [p for p in parts if p.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
            if len(image_names) > 1:
                # Eğer bir önceki galeriden resim birikmişse finalize edelim
                if galeri_resimleri:
                    with open(os.path.join("../static", "gallery.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        galeri_sablon_icerigi = sablon_dosyasi.read()
                    galeri_resim_html_listesi = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    galeri_modul_icerigi = galeri_sablon_icerigi.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(galeri_resim_html_listesi))
                    html_icerik_parcalari.append(galeri_modul_icerigi)
                    galeri_resimleri = []
                # Bu satırdaki tüm görselleri galeri olarak işle
                with open(os.path.join("../static", "gallery.html"), "r", encoding="utf-8") as sablon_dosyasi:
                    galeri_sablon_icerigi = sablon_dosyasi.read()
                galeri_resim_html_listesi = [f'<img src="{img}" alt="Proje Galeri Resmi">' for img in image_names]
                galeri_modul_icerigi = galeri_sablon_icerigi.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(galeri_resim_html_listesi))
                html_icerik_parcalari.append(galeri_modul_icerigi)
                continue

            # Satır tek görsel içeriyorsa
            elif len(image_names) == 1:
                # Eğer önceden bir galeri birikmişse finalize edelim
                if galeri_resimleri:
                    with open(os.path.join("../static", "gallery.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        galeri_sablon_icerigi = sablon_dosyasi.read()
                    galeri_resim_html_listesi = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                    galeri_modul_icerigi = galeri_sablon_icerigi.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(galeri_resim_html_listesi))
                    html_icerik_parcalari.append(galeri_modul_icerigi)
                    galeri_resimleri = []
                with open(os.path.join("../static", "image.html"), "r", encoding="utf-8") as sablon_dosyasi:
                    resim_sablon_icerigi = sablon_dosyasi.read()
                resim_modul_icerigi = resim_sablon_icerigi.replace("{% block resim_url %}{% endblock %}", image_names[0])
                html_icerik_parcalari.append(resim_modul_icerigi)
                continue

            # Video linkleri kontrolü
            if satir.lower().startswith(("https://vimeo.com", "https://youtube.be", "https://youtu.be")):
                video_url = satir
                if "vimeo.com" in video_url:
                    video_id = video_url.split("/")[-1]
                    with open(os.path.join("../static", "vimeo.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        video_sablon_icerigi = sablon_dosyasi.read()
                    video_modul_icerigi = video_sablon_icerigi.replace("{% block video_id %}{% endblock %}", video_id)
                    html_icerik_parcalari.append(video_modul_icerigi)
                elif "youtube.be" in video_url or "youtu.be" in video_url or "youtube.com" in video_url:
                    video_id = video_url.split("=")[-1] if "=" in video_url else video_url.split("/")[-1]
                    with open(os.path.join("../static", "youtube.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        video_sablon_icerigi = sablon_dosyasi.read()
                    video_modul_icerigi = video_sablon_icerigi.replace("{% block video_id %}{% endblock %}", video_id)
                    html_icerik_parcalari.append(video_modul_icerigi)
                continue

            # Link kontrolü
            elif "http://" in satir.lower() or "https://" in satir.lower():
                link_eslesme = re.search(r"^(.*?)\s+(https?://\S+)", satir)
                if link_eslesme:
                    link_metni = link_eslesme.group(1).strip()
                    link_url = link_eslesme.group(2).strip()
                    with open(os.path.join("../static", "link.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        link_sablon_icerigi = sablon_dosyasi.read()
                    link_modul_icerigi = link_sablon_icerigi.replace("{% block link_url %}", link_url)
                    link_modul_icerigi = link_modul_icerigi.replace("{% block link_metni %}", link_metni)
                    html_icerik_parcalari.append(link_modul_icerigi)
                else:
                    print("DEBUG: Regex EŞLEŞMEDİ!")
                    html_icerik_parcalari.append(f"<p>{satir}</p>")
                continue

            # Metin/paragraf satırı ise
            else:
                paragraf_satirlari.append(satir)
                if satir.endswith(('.', '!', '?')):
                    with open(os.path.join("../static", "text.html"), "r", encoding="utf-8") as sablon_dosyasi:
                        paragraf_sablon_icerigi = sablon_dosyasi.read()
                    paragraf_modul_icerigi = paragraf_sablon_icerigi.replace("{% block content %}{% endblock %}", " ".join(paragraf_satirlari))
                    html_icerik_parcalari.append(paragraf_modul_icerigi)
                    paragraf_satirlari = []
                    # Eğer bu satırın gelmesiyle bir galerinin kapanması gerekiyorsa finalize edelim
                    if galeri_resimleri:
                        with open(os.path.join("../static", "gallery.html"), "r", encoding="utf-8") as sablon_dosyasi:
                            galeri_sablon_icerigi = sablon_dosyasi.read()
                        galeri_resim_html_listesi = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
                        galeri_modul_icerigi = galeri_sablon_icerigi.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(galeri_resim_html_listesi))
                        html_icerik_parcalari.append(galeri_modul_icerigi)
                        galeri_resimleri = []

        # Döngü bittikten sonra kalan galeri veya paragraf varsa finalize et
        if galeri_resimleri:
            with open(os.path.join("../static", "gallery.html"), "r", encoding="utf-8") as sablon_dosyasi:
                galeri_sablon_icerigi = sablon_dosyasi.read()
            galeri_resim_html_listesi = [f'<img src="{resim}" alt="Proje Galeri Resmi">' for resim in galeri_resimleri]
            galeri_modul_icerigi = galeri_sablon_icerigi.replace("{% block galeri_resimleri %}{% endblock %}", "\n".join(galeri_resim_html_listesi))
            html_icerik_parcalari.append(galeri_modul_icerigi)
        if paragraf_satirlari:
            with open(os.path.join("../static", "text.html"), "r", encoding="utf-8") as sablon_dosyasi:
                paragraf_sablon_icerigi = sablon_dosyasi.read()
            paragraf_modul_icerigi = paragraf_sablon_icerigi.replace("{% block content %}{% endblock %}", " ".join(paragraf_satirlari))
            html_icerik_parcalari.append(paragraf_modul_icerigi)

    # Proje şablon dosyasını (project.html) oku
    with open(os.path.join("../static", "project.html"), "r", encoding="utf-8") as sablon_dosyasi:
        proje_sablon_icerigi = sablon_dosyasi.read()

    # Şablonu içerikle birleştir
    html_icerik = proje_sablon_icerigi.replace("{% block proje_icerigi %}{% endblock %}", "\n".join(html_icerik_parcalari))
    html_icerik = html_icerik.replace("{% block title %}{% endblock %}", proje_basligi)

    with open(index_html_yolu, "w", encoding="utf-8") as f:
        f.write(html_icerik)
    return True


def ana_sayfayi_Guncelle(proje_listesi):
    """Ana sayfayı proje listesiyle günceller (proje isimleri geri eklendi, üst dizinde arama, farklı thumbnail formatları desteği)."""

    proje_listesi_html_satirlari = [] # Proje listesi HTML satırlarını saklayacağımız liste

    def txt_dosyasi_numarasini_al(proje_bilgisi): # YARDIMCI FONKSİYON: .txt dosyasının numarasını alır
        txt_dosyasi_adi = proje_bilgisi["txt_dosyasi"] # .txt dosyası adını al
        numara_str = re.findall(r'\d+', txt_dosyasi_adi)[0] # .txt dosya adındaki ilk sayıyı (numarayı) bul
        return int(numara_str) # Sayıyı integer'a çevir

    sirali_proje_listesi = sorted(proje_listesi, key=txt_dosyasi_numarasini_al) # Projeleri .txt numarasına göre sırala

    for proje_bilgisi in sirali_proje_listesi: # Sıralı proje listesini döngüye al
        klasor_adi = proje_bilgisi["klasor_adi"] # Proje klasör adı
        txt_dosyasi_adi = proje_bilgisi["txt_dosyasi"] # Proje txt dosyası adı

        proje_klasor_yolu = os.path.join("..", klasor_adi) # Proje klasör yolu (moi ana dizinine göre - ÜST DİZİN ".."!)
        txt_dosya_yolu = os.path.join(proje_klasor_yolu, txt_dosyasi_adi) # txt dosyasının tam yolu


        thumbnail_dosya_adi = None # Başlangıçta thumbnail dosya adı yok
        thumbnail_dosya_yolu = None # Başlangıçta thumbnail dosya yolu yok


        for dosya_adi in os.listdir(proje_klasor_yolu):  
            if dosya_adi.lower().startswith("thumbnail.") and dosya_adi.lower().endswith((".jpg", ".jpeg", ".gif", ".png")):  
                thumbnail_dosya_adi = dosya_adi  
                thumbnail_dosya_yolu = os.path.join(proje_klasor_yolu, thumbnail_dosya_adi)  

                # Görselin genişlik ve yüksekliğini al
                with Image.open(thumbnail_dosya_yolu) as img:
                    genislik, yukseklik = img.size  # (width, height)

                break  # İlk bulunan thumbnail'i kullan ve döngüden çık


        with open(txt_dosya_yolu, "r", encoding="utf-8") as f: # .txt dosyasını UTF-8 kodlamasıyla aç
            proje_basligi = f.readline().strip() # .txt dosyasının ilk satırını proje başlığı olarak oku


        if thumbnail_dosya_yolu and os.path.exists(thumbnail_dosya_yolu): # Thumbnail dosyası bulundu ve gerçekten var mı kontrolü (GÜNCEL KOŞUL)
            thumbnail_url = f"{klasor_adi}/{thumbnail_dosya_adi}" # Thumbnail URL'i (GÜNCEL - dosya adını kullanıyor)
            proje_linki = f"{klasor_adi}" # Proje index.html linki

            proje_listesi_html_satiri = f"""<div class="brick"><a href="{proje_linki}"><img src="{thumbnail_url}" alt="{proje_basligi}" width="{genislik}" height="{yukseklik}"></a></div>""" # Proje listesi HTML satırını thumbnail ve proje başlığı ile oluştur - GÜNCELLENDİ
            proje_listesi_html_satirlari.append(proje_listesi_html_satiri) # HTML satırını listeye ekle
        else: # Eğer thumbnail dosyası yoksa
            print(f"  >> UYARI: {klasor_adi} klasöründe thumbnail için uygun dosya (thumbnail.jpg, .jpeg, .gif, .png) bulunamadı, proje ana sayfaya eklenmiyor.") # Konsola uyarı mesajı yazdır - GÜNCELLENEN UYARI MESAJI
            continue # Bu proje için döngüyü atla ve sonraki projeye geç


    # Ana sayfa şablon dosyasını (index.html) oku
    with open(os.path.join("../static", "index.html"), "r", encoding="utf-8") as sablon_dosyasi: # Şablon dosyasını UTF-8 ile aç
        ana_sayfa_sablon_icerigi = sablon_dosyasi.read() # Şablon içeriğini oku

    # Şablonu proje listesiyle birleştir
    ana_sayfa_html_icerigi = ana_sayfa_sablon_icerigi.replace("{% block proje_listesi_icerigi %}{% endblock %}", "\n".join(proje_listesi_html_satirlari)) # Proje listesi bloğunu doldur

    ana_sayfa_index_html_yolu = os.path.join("..", "index.html") # Ana sayfa index.html yolu (moi ana dizini - ÜST DİZİN ".."!)

    with open(ana_sayfa_index_html_yolu, "w", encoding="utf-8") as f: # Ana sayfa index.html dosyasını yazma modunda aç
        f.write(ana_sayfa_html_icerigi) # Oluşturulan HTML içeriğini dosyaya yaz

    print("Bitti!") # Konsola tamamlama mesajı yazdır
    return True # Başarılı şekilde oluşturulduğunu belirt

def ana_dongu():
    """Ana döngü: Klasörleri tara, index.html oluştur, ana sayfayı güncelle."""
    #baslangic_zamani = datetime.datetime.now()
    os.system('clear')
    proje_listesi = klasorleri_Tara("..") # Proje klasörlerini tara - ANA DİZİN ".." OLARAK GÜNCELLENDİ!
    #print("Proje Listesi:", proje_listesi) # Proje listesini yazdır - YENİ SATIR (GEÇİCİ - İsteğe Bağlı, Hata Ayıklama İçin Eklendi)
    # print(f"Toplam {len(proje_listesi)} proje bulundu.")

    for proje_bilgisi in proje_listesi:
        index_html_olusturuldu = index_html_Olustur(proje_bilgisi) # Her proje için index.html oluştur
        #if index_html_olusturuldu: # Artık her proje sonrası ana sayfayı GÜNCELLEMİYORUZ!
        #    ana_sayfayi_Guncelle(proje_listesi) # Ana sayfayı GÜNCELLE - HER PROJE SONRASINDA GÜNCELLENECEK! - SATIR YERİ DEĞİŞTİRİLDİ

    ana_sayfayi_Guncelle(proje_listesi) # Ana sayfayı GÜNCELLE - TÜM PROJELER BİTTİKTEN SONRA SADECE BİR KEZ GÜNCELLENECEK! - YENİ YERİ

    # bitis_zamani = datetime.datetime.now()
    # gecen_sure = bitis_zamani - baslangic_zamani
    # print(f"--- Proje Üretim Döngüsü Tamamlandı ({gecen_sure.seconds} saniye) ---")

if __name__ == "__main__":
    ana_dongu() # Ana döngüyü başlat