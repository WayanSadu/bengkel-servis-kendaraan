"""Sistem sederhana pengelolaan servis bengkel kendaraan."""

from abc import ABC, abstractmethod

from exceptions import (
    AturanBisnisError,
    BengkelError,
    DataTidakValidError,
    StokTidakCukupError,
)


def validasi_teks(nilai, nama_field):
    if not isinstance(nilai, str) or not nilai.strip():
        raise DataTidakValidError(f"{nama_field} wajib diisi dengan teks.")
    return nilai.strip()


def validasi_uang(nilai, nama_field):
    if type(nilai) is not int or nilai <= 0:
        raise DataTidakValidError(
            f"{nama_field} harus berupa bilangan bulat positif."
        )
    return nilai


class Kendaraan(ABC):
    def __init__(self, plat_nomor, merek):
        self.plat_nomor = plat_nomor
        self.merek = merek

    @property
    def plat_nomor(self):
        return self.__plat_nomor

    @plat_nomor.setter
    def plat_nomor(self, nilai):
        self.__plat_nomor = validasi_teks(nilai, "Plat nomor").upper()

    @property
    def merek(self):
        return self.__merek

    @merek.setter
    def merek(self, nilai):
        self.__merek = validasi_teks(nilai, "Merek kendaraan")

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

    def tarif_jasa(self, layanan):
        if not isinstance(layanan, Layanan):
            raise DataTidakValidError("Objek layanan yang diberikan tidak valid.")
        return layanan.tarif_dasar * self.FAKTOR_JASA


class Mobil(Kendaraan):
    FAKTOR_JASA = 2

    def tarif_jasa(self, layanan):
        if not isinstance(layanan, Layanan):
            raise DataTidakValidError("Objek layanan yang diberikan tidak valid.")
        return layanan.tarif_dasar * self.FAKTOR_JASA


class Pelanggan:
    def __init__(self, kode, nama, member=False):
        self.kode = validasi_teks(kode, "Kode pelanggan")
        self.nama = validasi_teks(nama, "Nama pelanggan")

        if type(member) is not bool:
            raise DataTidakValidError("Status member harus berupa True atau False.")

        self.member = member


class Mekanik:
    def __init__(self, kode, nama):
        self.kode = validasi_teks(kode, "Kode mekanik")
        self.nama = validasi_teks(nama, "Nama mekanik")


class Layanan:
    def __init__(self, kode, nama, tarif_dasar):
        self.kode = validasi_teks(kode, "Kode layanan")
        self.nama = validasi_teks(nama, "Nama layanan")
        self.tarif_dasar = tarif_dasar

    @property
    def tarif_dasar(self):
        return self.__tarif_dasar

    @tarif_dasar.setter
    def tarif_dasar(self, nilai):
        self.__tarif_dasar = validasi_uang(nilai, "Tarif jasa")


class SukuCadang:
    def __init__(self, kode, nama, harga, stok):
        self.kode = validasi_teks(kode, "Kode suku cadang")
        self.nama = validasi_teks(nama, "Nama suku cadang")
        self.harga = harga
        self.stok = stok

    @property
    def harga(self):
        return self.__harga

    @harga.setter
    def harga(self, nilai):
        self.__harga = validasi_uang(nilai, "Harga suku cadang")

    @property
    def stok(self):
        return self.__stok

    @stok.setter
    def stok(self, nilai):
        if type(nilai) is not int or nilai < 0:
            raise DataTidakValidError(
                "Stok harus berupa bilangan bulat nol atau lebih."
            )
        self.__stok = nilai

    def ambil(self, jumlah):
        if type(jumlah) is not int or jumlah <= 0:
            raise DataTidakValidError(
                "Jumlah suku cadang harus berupa bilangan bulat positif."
            )

        if jumlah > self.stok:
            raise StokTidakCukupError(
                f"Stok {self.nama} tidak cukup: tersedia {self.stok}, "
                f"diminta {jumlah}."
            )

        self.stok -= jumlah


class RincianWorkOrder:
    def __init__(self):
        self.jasa = []
        self.suku = []

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

    def hitung_diskon(self, jasa, member):
        if member:
            return jasa * self.PERSEN_MEMBER // 100
        return 0


class WorkOrder(DiskonJasaMixin):
    jumlah_dibuat = 0

    URUTAN_STATUS = {
        "antre": "dikerjakan",
        "dikerjakan": "selesai",
        "selesai": "dibayar",
    }

    def __init__(self, pelanggan, kendaraan, mekanik):
        if not isinstance(pelanggan, Pelanggan):
            raise DataTidakValidError(
                "Work order memerlukan pelanggan yang valid."
            )
        if not isinstance(kendaraan, Kendaraan):
            raise DataTidakValidError(
                "Work order memerlukan kendaraan yang valid."
            )
        if not isinstance(mekanik, Mekanik):
            raise DataTidakValidError(
                "Work order memerlukan mekanik yang valid."
            )

        super().__init__()

        WorkOrder.jumlah_dibuat += 1
        self.nomor = f"WO{WorkOrder.jumlah_dibuat:03d}"
        self.pelanggan = pelanggan
        self.kendaraan = kendaraan
        self.mekanik = mekanik
        self.__status = "antre"
        self.rincian = RincianWorkOrder()

    @property
    def status(self):
        return self.__status

    def ubah_status(self, tujuan):
        tujuan = validasi_teks(tujuan, "Status tujuan").lower()

        if self.URUTAN_STATUS.get(self.status) != tujuan:
            raise AturanBisnisError(
                f"Urutan status tidak valid: '{self.status}' ke '{tujuan}'."
            )

        self.__status = tujuan

    def _pastikan_sedang_dikerjakan(self):
        if self.status != "dikerjakan":
            raise AturanBisnisError(
                "Jasa dan suku cadang hanya boleh ditambahkan saat "
                "work order berstatus 'dikerjakan'."
            )

    def tambah_layanan(self, layanan):
        self._pastikan_sedang_dikerjakan()

        if not isinstance(layanan, Layanan):
            raise DataTidakValidError("Objek layanan yang diberikan tidak valid.")

        tarif = self.kendaraan.tarif_jasa(layanan)
        self.rincian.tambah_jasa(layanan, tarif)

    def pakai_suku(self, suku, jumlah):
        self._pastikan_sedang_dikerjakan()

        if not isinstance(suku, SukuCadang):
            raise DataTidakValidError(
                "Objek suku cadang yang diberikan tidak valid."
            )

        self.rincian.tambah_suku(suku, jumlah)

    def total(self):
        jasa = self.rincian.subtotal_jasa()
        diskon = self.hitung_diskon(jasa, self.pelanggan.member)
        return jasa - diskon + self.rincian.subtotal_suku()

    def __str__(self):
        return f"{self.nomor} | {self.status} | {self.kendaraan}"


def main():
    try:
        pelanggan = Pelanggan("P01", "Ayu", True)
        motor = Motor.dari_data("DK1234AB", "Honda")
        mobil = Mobil("DK5678CD", "Toyota")
        mekanik = Mekanik("M01", "Budi")

        ganti_oli = Layanan("L01", "Ganti oli", 40_000)
        perbaikan_rem = Layanan("L02", "Perbaikan rem", 60_000)

        oli = SukuCadang("S01", "Oli", 50_000, 10)
        filter_oli = SukuCadang("S02", "Filter oli", 25_000, 5)

        print(f"Tarif ganti oli motor: Rp{motor.tarif_jasa(ganti_oli):,}")
        print(f"Tarif ganti oli mobil: Rp{mobil.tarif_jasa(ganti_oli):,}")

        wo = WorkOrder(pelanggan, motor, mekanik)
        print(wo)

        wo.ubah_status("dikerjakan")
        wo.tambah_layanan(ganti_oli)
        wo.tambah_layanan(perbaikan_rem)
        wo.pakai_suku(oli, 1)
        wo.pakai_suku(filter_oli, 1)

        wo.ubah_status("selesai")

        jasa = wo.rincian.subtotal_jasa()
        diskon = wo.hitung_diskon(jasa, pelanggan.member)

        print(wo)
        print(f"Mekanik: {wo.mekanik.nama}")
        print(f"Jasa / diskon: Rp{jasa:,} / Rp{diskon:,}")
        print(f"Suku cadang: Rp{wo.rincian.subtotal_suku():,}")
        print(f"Total: Rp{wo.total():,}")

        wo.ubah_status("dibayar")
        print(wo)
        print(f"Stok oli/filter: {oli.stok}/{filter_oli.stok}")

    except BengkelError as error:
        print(f"Transaksi tidak dapat diproses: {error}")
    else:
        print("Transaksi work order berhasil diproses.")
    finally:
        print("Proses transaksi selesai.")

    # Contoh exception karena stok yang diminta melebihi persediaan.
    try:
        oli.ambil(100)
    except StokTidakCukupError as error:
        print(f"Validasi stok berhasil menolak permintaan: {error}")

    # Contoh exception karena nilai stok tidak valid.
    try:
        oli.stok = -1
    except DataTidakValidError as error:
        print(f"Validasi stok berhasil menolak data: {error}")


if __name__ == "__main__":
    main()