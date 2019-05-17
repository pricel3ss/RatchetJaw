from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm, PostRateForm, SearchRatesForm, LocationReviewForm, MessageForm
from app.models import User, Post, Rate, LocationReview, City, Message, Notification
from app.translate import translate
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})




@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)



states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

@bp.route('/post_rate', methods=['POST','GET'])
@login_required
def post_rate():
    form = PostRateForm()
    if form.validate_on_submit():
        rate = Rate(equipment_type=form.equipment_type.data,
                    hazardous_freight=form.hazardous_freight.data,
                    origin=form.origin.data,
                    destination=form.destination.data,
                    brokered_load=form.brokered_load.data,
                    weather=form.weather.data,
                    rate_per_mile=form.rate_per_mile.data,
                    deadhead=form.dead_head.data,
                    author=current_user)
        db.session.add(rate)
        db.session.commit()
        flash(_('Your rate has been saved.'))
        return redirect(url_for('main.index'))
    return render_template('post_rate.html', title=_('Post Rate'),
                           form=form)



@bp.route('/search_rate', methods=['POST','GET'])
@login_required
def search_rates():
    form = SearchRatesForm()
    if form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        rates = Rate.query.filter(Rate.origin==form.origin.data,
                                  Rate.destination == form.destination.data,
                                  Rate.equipment_type == form.equipment_type.data).order_by(Rate.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)

        next_url = url_for('main.user', username=user.username,
                           page=rates.next_num) if rates.has_next else None
        prev_url = url_for('main.user', username=user.username,
                           page=rates.prev_num) if rates.has_prev else None
        return render_template('search_rates_screen.html', user=user, rates=rates.items,
                               next_url=next_url, prev_url=prev_url, form=form)

    return render_template('search_rates_screen.html',
                           form=form)


@bp.route('/post_review', methods=['POST','GET'])
@login_required
def post_review():
    form = LocationReviewForm()

    return render_template('post_review.html', title=_('Post Review'), form=form)



@bp.route('/review_handler', methods=['POST','GET'])
@login_required
def review_handler():
    shipper = request.form['shipper']
    unloading_score = request.form['unloading_score']
    lateness_score = request.form['lateness_score']
    comments = request.form['comments']
    consignee = request.form['consignee']

    address = request.form['autocomplete']
    street_number = request.form['street_number']
    street_name = request.form['route']
    city = request.form['locality']
    state = request.form['state']
    country = request.form['country']
    zip_code = request.form['postal_code']

    review = LocationReview(
                address=address,
                city=city,
                state=state,
                zip=zip_code,
                country=country,
                consignee=consignee,
                comments=comments,
                unloading_score=unloading_score,
                shipper=shipper,
                author=current_user,
                lateness_score=lateness_score)

    db.session.add(review)
    db.session.commit()
    flash(_('You have posted a review!'))
    return redirect(url_for('main.index'))



@bp.route('/search_review', methods=['POST','GET'])
@login_required
def search_review():
    return render_template('search_reviews_screen.html', title=_('Search Reviews'))



@bp.route('/search_review_handler', methods=['POST','GET'])
@login_required
def search_review_handler():
    address = request.form['autocomplete']
    page = request.args.get('page', 1, type=int)
    reviews = LocationReview.query.filter_by(address=address).order_by(LocationReview.Date.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)


    next_url = url_for('main.user', username=user.username,
                       page=reviews.next_num) if reviews.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=reviews.prev_num) if reviews.has_prev else None
    return render_template('search_reviews_screen_full.html', user=user, reviews=reviews.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    query = db.session.query(City.full_city_name).filter(City.full_city_name.like('%' + str(search) + '%'))
    results = []
    for mv in query:
        results.append(mv[0])
    results = [mv[0] for mv in query.all()]
    return jsonify(matching_results=results)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))
# query = db.session.query(City.full_city_name)
