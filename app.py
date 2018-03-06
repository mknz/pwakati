# -*- coding: utf-8 -*-

import argparse
import os

from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired

import decompose


class ConfigError(Exception):
    pass


SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise ConfigError

app = Flask(__name__)
app.config.from_object(__name__)


class MyForm(FlaskForm):
    text = TextAreaField('テキストを入力', validators=[DataRequired()])


def preprocess_input(istr):
    istr = istr.replace('\r', '')
    return istr


@app.route('/', methods=('GET', 'POST'))
def pwakati():
    form = MyForm()
    if form.validate_on_submit():
        rstr = decompose.main(preprocess_input(form.text.data))
        return render_template('pwakati.html', form=form, rstr=rstr)
    return render_template('pwakati.html', form=form)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pwakati')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--port', type=int)
    args = parser.parse_args()

    app.run(port=args.port, debug=args.debug)
