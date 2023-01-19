from flask import flash, redirect, render_template, request

from . import app, db
from .forms import YacutForm
from .models import URLMap
from .utils import get_unique_short


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = YacutForm()
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        if not custom_id:
            custom_id = get_unique_short()
        elif URLMap.query.filter_by(short=custom_id).first():
            form.custom_id.errors = [f'Имя {custom_id} уже занято!']
            return render_template('yacut.html', form=form)
        url_map = URLMap(
            original=form.original_link.data,
            short=custom_id,
        )
        db.session.add(url_map)
        db.session.commit()
        flash(f'Ваша новая ссылка готова: '
              f'<a href="{request.base_url}{custom_id}">'
              f'{request.base_url}{custom_id}</a>')
    return render_template('yacut.html', form=form)


@app.route('/<string:short>', methods=['GET'])
def yacat_redirect(short):
    return redirect(
        URLMap.query.filter_by(short=short).first_or_404().original)
