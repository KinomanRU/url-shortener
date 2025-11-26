from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "t_link"
    slug: Mapped[str] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(unique=True)
