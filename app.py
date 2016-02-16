# -*- coding: utf-8 -*-
import decompose
from flask import Flask, render_template
from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
import sys, random

SECRET_KEY = 'DEVELOPMENT_KEY'

app = Flask(__name__)
app.config.from_object(__name__)

class MyForm(Form):
    text = TextAreaField(u'テキストを入力', validators=[DataRequired()])

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

if __name__ == "__main__":
    port = int(sys.argv[1])

    if len(sys.argv) > 2 and sys.argv[2] == 'debug':
        print "Run in debug mode."
        debug = True
    else:
        debug = False

    app.run(host="0.0.0.0", port=port, debug=debug)

