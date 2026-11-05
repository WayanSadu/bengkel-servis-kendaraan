"""Custom exception untuk aplikasi bengkel servis kendaraan."""


class BengkelError(Exception):
    """Base exception untuk seluruh kesalahan aplikasi bengkel."""


class DataTidakValidError(BengkelError):
    """Data yang diberikan tidak sesuai format atau nilai yang diwajibkan."""


class AturanBisnisError(BengkelError):
    """Operasi yang diminta melanggar aturan bisnis bengkel."""


class StokTidakCukupError(AturanBisnisError):
    """Stok suku cadang tidak cukup untuk memenuhi permintaan."""