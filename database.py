from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db
import hashlib

def utc_now():
    return datetime.now(timezone.utc)

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)

    # Dates
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False)

    # Author
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    # Gallery
    gallery = relationship("Gallery", back_populates="post", uselist=False, cascade="all, delete-orphan")

class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)

    # Dates
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    github_url: Mapped[str] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False)

    # Author
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="projects")

    # Gallery
    gallery = relationship("Gallery", back_populates="project", uselist=False, cascade="all, delete-orphan")

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

    # Professional Identity
    job_title: Mapped[str] = mapped_column(String(250), nullable=True)
    pronoun: Mapped[str] = mapped_column(String(250), nullable=False)
    tagline: Mapped[str] = mapped_column(String(500), nullable=True)

    # Bio & Location
    about: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=True)

    # Links & Assets
    linkedin: Mapped[str] = mapped_column(String(500), nullable=False)
    github: Mapped[str] = mapped_column(String(500), nullable=False)
    profile_img: Mapped[str] = mapped_column(String(500), nullable=True)
    resume_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Is Admin?
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dates
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=True
    )

    # Relationships
    posts = relationship("Post", back_populates="author")
    projects = relationship("Project", back_populates="author")

    @property
    def avatar_url(self):
        if self.profile_img:
            return self.profile_img

        email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200"


class Skill(db.Model):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    icon_class: Mapped[str] = mapped_column(String(250), nullable=False)

    # Dates
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=True
    )


class Gallery(db.Model):

    __tablename__ = "galleries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    post_id: Mapped[int | None] = mapped_column(
        Integer, db.ForeignKey("posts.id"), nullable=True)
    project_id: Mapped[int | None] = mapped_column(
        Integer, db.ForeignKey("projects.id"), nullable=True)

    post = relationship("Post", back_populates="gallery")
    project = relationship("Project", back_populates="gallery")

    images = relationship(
        "GalleryImage",
        back_populates="gallery",
        cascade="all, delete-orphan",
        order_by="GalleryImage.position"
    )

class GalleryImage(db.Model):
    __tablename__ = "gallery_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    alt_text: Mapped[str] = mapped_column(String(250), nullable=False)
    gallery_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("galleries.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    gallery = relationship("Gallery", back_populates="images")