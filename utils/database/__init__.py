import asyncpg

class Record(asyncpg.Record):
    """
    Subclass dari asyncpg.Record untuk memudahkan akses data dengan dot notation.

    Contoh:
        result = await db.fetchrow("SELECT name FROM users WHERE id = $1", user_id)
        print(result.name)  # Bisa langsung pakai .name, bukan result["name"]
    """
    def __getattr__(self, attr: str):
        return self.get(attr)

async def setup(pool: asyncpg.Pool) -> asyncpg.Pool:
    """
    Menyiapkan koneksi database dengan menjalankan perintah SQL dari file schema.sql.

    Fungsi ini membaca isi file `schema.sql`, kemudian mengeksekusi isi file tersebut
    ke dalam database melalui koneksi pool.

    Args:
        pool (asyncpg.Pool): Pool koneksi database yang sudah dibuat.

    Returns:
        asyncpg.Pool: Pool yang sama, setelah menjalankan skema database.
    """
    
    with open("utils/database/schema.sql", "r", encoding="UTF-8") as buffer:
        schema = buffer.read()
        await pool.execute(schema)

    return pool

async def connect(**kwargs):
    """
    Membuat koneksi ke database PostgreSQL menggunakan asyncpg dengan custom Record class.

    Fungsi ini menggunakan parameter koneksi seperti host, user, password, dan lainnya,
    lalu membuat connection pool ke database. Jika berhasil, fungsi ini juga menjalankan
    setup untuk inisialisasi skema database.

    Args:
        **kwargs: Parameter koneksi seperti host, database, user, password, dll.

    Returns:
        asyncpg.Pool: Pool koneksi database yang telah di-setup.

    Raises:
        Exception: Jika gagal membuat pool koneksi.
    """

    kwargs['record_class'] = Record 
    
    pool = await asyncpg.create_pool(
        **kwargs,
        statement_cache_size=0,
    )

    if not pool:
        raise Exception("Tidak dapat membuat koneksi ke PostgreSQL")

    return await setup(pool)