from flask import flash, redirect, render_template, abort

from . import app
from settings import Config
from .models import URLMap
from .forms import UrlForm
from .exceptions import NotUniqShortLink
from .utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = UrlForm()
    if form.validate_on_submit():
        try:
            short_url = get_unique_short_id(
                Config.SHORT_URL_LENGTH,
                form.original_link.data,
                form.custom_id.data,
            )
        except NotUniqShortLink:
            flash(f'Имя {form.custom_id.data} уже занято!')
            return render_template('index.html', form=form)
        flash(f'Ссылка успешно добавлена. Короткая ссылка: <a href="{short_url}">{short_url}</a>')
        return render_template('index.html', form=form)
    return render_template('index.html', form=form)


@app.route('/<string:short_id>')
def url_redirect(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        abort(404)
    return redirect(url_map.original, code=302)
