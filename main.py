from abc import ABC, abstractmethod
 
class Kendaraan(ABC):
    def __init__(self, plat_nomor, merek):
        self.plat_nomor, self._merek = plat_nomor.upper(), merek
    @property
    def merek(self):
        return self._merek
    @abstractmethod
    def tarif_jasa(self, layanan):
        raise NotImplementedError
    @classmethod
    def dari_data(cls, plat_nomor, merek):
        return cls(plat_nomor, merek)
    def __str__(self):
        return f"{type(self).__name__} {self.plat_nomor}"
    def __eq__(self, lain):
        return type(self) is type(lain) and self.plat_nomor == lain.plat_nomor
 
class Motor(Kendaraan):
    FAKTOR_JASA = 1
    def __init__(self, plat_nomor, merek):
        super().__init__(plat_nomor, merek)
    def tarif_jasa(self, layanan):
        return layanan.tarif_dasar * self.FAKTOR_JASA
 
class Mobil(Kendaraan):
    FAKTOR_JASA = 2
    def __init__(self, plat_nomor, merek):
        super().__init__(plat_nomor, merek)
    def tarif_jasa(self, layanan):
        return layanan.tarif_dasar * self.FAKTOR_JASA
 
class Pelanggan:
    def __init__(self, kode, nama, member=False):
        self.kode, self.nama, self.member = kode, nama, member
 
class Mekanik:
    def __init__(self, kode, nama):
        self.kode, self.nama = kode, nama
 
class Layanan:
    def __init__(self, kode, nama, tarif_dasar):
        self.kode, self.nama = kode, nama
        self.tarif_dasar = tarif_dasar
    @property
    def tarif_dasar(self):
        return self.__tarif_dasar
    @tarif_dasar.setter
    def tarif_dasar(self, nilai):
        if type(nilai) is not int or nilai <= 0:
            raise ValueError("Tarif jasa harus positif.")
        self.__tarif_dasar = nilai
 
class SukuCadang:
    def __init__(self, kode, nama, harga, stok):
        self.kode, self.nama = kode, nama
        self.harga, self.stok = harga, stok
    @property
    def harga(self):
        return self.__harga
    @harga.setter
    def harga(self, nilai):
        if type(nilai) is not int or nilai <= 0:
            raise ValueError("Harga suku cadang harus positif.")
        self.__harga = nilai
    @property
    def stok(self):
        return self.__stok
    @stok.setter
    def stok(self, nilai):
        if type(nilai) is not int or nilai < 0:
            raise ValueError("Stok tidak valid.")
        self.__stok = nilai
    @staticmethod
    def jumlah_valid(jumlah):
        return type(jumlah) is int and jumlah > 0
    def ambil(self, jumlah):
        if not self.jumlah_valid(jumlah) or jumlah > self.stok:
            raise ValueError("Jumlah tidak valid atau stok kurang.")
        self.stok -= jumlah
 
class RincianWorkOrder:
    def __init__(self):
        self.jasa, self.suku = [], []
    def tambah_jasa(self, layanan, tarif):
        self.jasa.append((layanan, tarif))
    def tambah_suku(self, suku, jumlah):
        suku.ambil(jumlah)
        self.suku.append((suku, jumlah, suku.harga))
    def subtotal_jasa(self):
        return sum(tarif for _, tarif in self.jasa)
    def subtotal_suku(self):
        return sum(jumlah * harga for _, jumlah, harga in self.suku)
 
class DiskonJasaMixin:
    PERSEN_MEMBER = 10
    def __init__(self):
        super().__init__()
    def hitung_diskon(self, jasa, member):
        return jasa * self.PERSEN_MEMBER // 100 if member else 0
 
class WorkOrder(DiskonJasaMixin):
    jumlah_dibuat = 0
    def __init__(self, pelanggan, kendaraan, mekanik):
        super().__init__()
        WorkOrder.jumlah_dibuat += 1
        self.nomor = f"WO{WorkOrder.jumlah_dibuat:03d}"
        self.pelanggan, self.kendaraan = pelanggan, kendaraan
        self.mekanik, self.__status = mekanik, "antre"
        self.rincian = RincianWorkOrder()
    @property
    def status(self):
        return self.__status
    def ubah_status(self, tujuan):
        berikut = {"antre": "dikerjakan", "dikerjakan": "selesai",
                   "selesai": "dibayar"}
        if berikut.get(self.status) != tujuan:
            raise ValueError("Urutan status tidak valid.")
        self.__status = tujuan
    def tambah_layanan(self, layanan):
        if self.status != "dikerjakan":
            raise ValueError("Work order harus dikerjakan.")
        tarif = self.kendaraan.tarif_jasa(layanan)
        self.rincian.tambah_jasa(layanan, tarif)
    def pakai_suku(self, suku, jumlah):
        if self.status != "dikerjakan":
            raise ValueError("Work order harus dikerjakan.")
        self.rincian.tambah_suku(suku, jumlah)
    def total(self):
        jasa = self.rincian.subtotal_jasa()
        diskon = self.hitung_diskon(jasa, self.pelanggan.member)
        return jasa - diskon + self.rincian.subtotal_suku()
    def __str__(self):
        return f"{self.nomor} | {self.status} | {self.kendaraan}"
 
if __name__ == "__main__":
    pelanggan = Pelanggan("P01", "Ayu", True)
    motor = Motor.dari_data("DK1234AB", "Honda")
    mobil = Mobil("DK5678CD", "Toyota")
    mekanik = Mekanik("M01", "Budi")
    ganti_oli = Layanan("L01", "Ganti oli", 40_000)
    rem = Layanan("L02", "Perbaikan rem", 60_000)
    oli = SukuCadang("S01", "Oli", 50_000, 10)
    filter_oli = SukuCadang("S02", "Filter oli", 25_000, 5)
    wo = WorkOrder(pelanggan, motor, mekanik)
    print(f"Jasa ganti oli mobil: Rp{mobil.tarif_jasa(ganti_oli):,}")
    print(wo)
    wo.ubah_status("dikerjakan")
    print(wo)
    wo.tambah_layanan(ganti_oli)
    wo.tambah_layanan(rem)
    wo.pakai_suku(oli, 1)
    wo.pakai_suku(filter_oli, 1)
    wo.ubah_status("selesai")
    print(wo)
    print(f"Mekanik: {wo.mekanik.nama}")
    jasa = wo.rincian.subtotal_jasa()
    diskon = wo.hitung_diskon(jasa, pelanggan.member)
    print(f"Jasa / diskon: Rp{jasa:,} / Rp{diskon:,}")
    print(f"Suku cadang: Rp{wo.rincian.subtotal_suku():,}")
    print(f"Total: Rp{wo.total():,}")
    wo.ubah_status("dibayar")
    print(wo)
    print(f"Stok oli/filter: {oli.stok}/{filter_oli.stok}")
    try:
        oli.stok = -1
    except ValueError as error:
        print(error)
    pembanding = Motor.dari_data("DK1234AB", "Honda")
    print(f"Kendaraan sama: {motor == pembanding}")