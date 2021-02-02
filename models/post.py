from database import db
from sqlalchemy import asc, desc

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def get_by_post_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all_posts_by_user(cls, user_id, page, per_page):
        return cls.query.filter_by(user_id=user_id).order_by(desc(cls.created_at)).paginate(page, per_page)

    @classmethod
    def get_all_posts(cls, page, per_page, order):
        if order == 'asc':
            order_logic = asc(cls.created_at)
        else:
            order_logic = desc(cls.created_at)
        return cls.query.order_by(order_logic).paginate(page=page, per_page=per_page)

    def data(self):
        return {'id': self.id, 'body': self.body, 'user_id': self.user_id}

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
