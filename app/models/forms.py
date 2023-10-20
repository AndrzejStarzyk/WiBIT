from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Nazwa użytkownika"})
    password1 = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Hasło"})
    password2 = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                              render_kw={"placeholder": "Powtórzenie hasła"})
    submit = SubmitField('Zarejestruj')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Nazwa użytkownika"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Hasło"})
    submit = SubmitField('Zaloguj')
