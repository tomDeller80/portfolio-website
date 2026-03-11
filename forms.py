from wtforms import StringField, SubmitField, PasswordField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Optional, Email, ValidationError, URL, Length, EqualTo
from flask_quill.fields import QuillField
from flask_wtf import FlaskForm

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = QuillField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_message(self, field):
        clean_data = field.data.replace('<p>', '').replace('</p>', '').replace('<br>', '').strip()

        if not clean_data:
            raise ValidationError("This field is required.")

class SetupForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long.")
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )

    # Professional Identity
    job_title = StringField('Job Title', validators=[DataRequired()])
    pronoun = StringField('Pronoun', validators=[DataRequired()])
    tagline = StringField('Tag Line', validators=[DataRequired()])

    # Bio & Location
    about = QuillField('About me', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])

    linkedin = StringField('LinkedIn', validators=[DataRequired(), URL()])
    github = StringField('Github', validators=[DataRequired(), URL()])
    profile_img = StringField('Profile Image', validators=[Optional(), URL()])
    resume_url = StringField('Resume Url', validators=[DataRequired(), URL()])

    is_admin = HiddenField('Is Admin', default='True')
    submit = SubmitField('Submit')

    def validate_about(self, field):
        clean_data = field.data.replace('<p>', '').replace('</p>', '').replace('<br>', '').strip()

        if not clean_data:
            raise ValidationError("This field is required.")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired(), URL()])
    tags = StringField('Tags',
                       validators=[DataRequired()],
                       render_kw={"placeholder": "Enter tags separated by commas..."})
    body = QuillField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_body(self, field):
        clean_data = field.data.replace('<p>', '').replace('</p>', '').replace('<br>', '').strip()

        if not clean_data:
            raise ValidationError("This field is required.")

class CreateProjectForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Project Image URL", validators=[DataRequired(), URL()])
    github_url = StringField("GitHub Repository URL", validators=[Optional(), URL()])
    demo_url = StringField("Live Demo URL", validators=[Optional(), URL()])
    tags = StringField('Tags',
                       validators=[DataRequired()],
                       render_kw={"placeholder": "Enter tags separated by commas..."})
    body = QuillField("Project Description", validators=[DataRequired()])
    submit = SubmitField("Submit Project")

    def validate_body(self, field):
        clean_data = field.data.replace('<p>', '').replace('</p>', '').replace('<br>', '').strip()

        if not clean_data:
            raise ValidationError("This field is required.")


class SkillForm(FlaskForm):
    name = StringField("Skill Name", validators=[DataRequired()])
    icon_class = StringField("DevIcon Class", validators=[DataRequired()])
    submit = SubmitField("Add Skill")
