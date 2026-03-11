from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean
from flask_login import UserMixin
from extensions import db
import hashlib

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    github_url: Mapped[str] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="projects")

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

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

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