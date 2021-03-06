#-*- coding: UTF-8 -*-
import cgi
from flask import render_template, request, redirect, url_for, json, session, abort
from xichuangzhu import app, db
from xichuangzhu.models.topic_model import Topic, TopicComment
from xichuangzhu.models.user_model import User
from xichuangzhu.form import TopicForm, CommentForm
from xichuangzhu.utils import require_login
# page topics
#--------------------------------------------------
@app.route('/topics')
def topics():
    page = int(request.args.get('page', 1))    
    pagination = Topic.query.order_by(Topic.create_time).paginate(page, 10)
    return render_template('topic/topics.html', pagination=pagination)

# page topic
#--------------------------------------------------
@app.route('/topic/<int:topic_id>')
def topic(topic_id):
    form = CommentForm()
    topic = Topic.query.get_or_404(topic_id)
    topic.click_num += 1
    db.session.add(topic)
    db.session.commit()    
    return render_template('topic/topic.html', topic=topic, form=form)

# proc - add comment
@app.route('/topic/<int:topic_id>/comment', methods=['POST'])
@require_login
def comment_topic(topic_id):
    form = CommentForm(request.form)    
    if form.validate():
        comment = TopicComment(content=cgi.escape(form.content.data), topic_id=topic_id, user_id=session['user_id'])
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('topic', topic_id=topic_id) + "#" + str(comment.id))
    else:
        return redirect(url_for('topic', topic_id=topic_id))

# page add topic
#--------------------------------------------------
@app.route('/topic/add', methods=['POST', 'GET'])
@require_login
def add_topic():
    if request.method == 'GET':
        form = TopicForm()
        return render_template('topic/add_topic.html', form=form)
    else:
        form = TopicForm(request.form)
        if form.validate():
            topic = Topic(title=cgi.escape(form.title.data), content=cgi.escape(form.content.data), user_id=session['user_id'])
            db.session.add(topic)
            db.session.commit()
            return redirect(url_for('topic', topic_id=topic.id))
        else:
            return render_template('topic/add_topic.html', form=form)

# page edit topic
#--------------------------------------------------
@app.route('/topic/edit/<int:topic_id>', methods=['POST', 'GET'])
@require_login
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if topic.user_id != session['user_id']:
        abort(404)

    if request.method == 'GET':
        form = TopicForm(title=topic.title, content=topic.content)
        return render_template('topic/edit_topic.html', topic=topic, form=form)
    else:
        form = TopicForm(request.form)
        if form.validate():
            topic.title = cgi.escape(form.title.data)
            topic.content = cgi.escape(form.content.data)
            db.session.add(topic)
            db.session.commit()
            return redirect(url_for('topic', topic_id=topic_id))
        else:
            return render_template('topic/edit_topic.html', topic=topic, form=form)