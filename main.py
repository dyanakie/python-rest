from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy, Model
import json

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)


class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Video(name = {self.name}, views = {self.views}, likes = {self.likes})"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# db.create_all()

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help='Please specify name of the video', required=True)
video_put_args.add_argument("views", type=int, help='Please specify views of the video', required=True)
video_put_args.add_argument("likes", type=int, help='Please specify likes of the video', required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Name of the video is required")
video_update_args.add_argument("views", type=int, help="Views of the video")
video_update_args.add_argument("likes", type=int, help="Likes on the video")

resource_fields = {
    'id': fields.Integer,
    "name": fields.String,
    "views": fields.Integer,
    "likes": fields.Integer
}

resource_fields_all = [{
    'id': fields.Integer,
    "name": fields.String,
    "views": fields.Integer,
    "likes": fields.Integer
}]


class GetAllVideos(Resource):
    # @marshal_with(resource_fields)
    def get(self):
        result = VideoModel.query.all()
        new_results = []
        # print(result)
        for index, modelObj in enumerate(result):
            new_results.append(modelObj.as_dict())

        print(new_results)
        return new_results


class Video(Resource):
    @marshal_with(resource_fields)
    def get(self, video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message='Not Found')
        return result

    @marshal_with(resource_fields)
    def put(self, video_id):
        if VideoModel.query.filter_by(id=video_id).first():
            abort(409, message='Such Id Already exists')
        args = video_put_args.parse_args()
        video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
        db.session.add(video)
        db.session.commit()
        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        args = video_update_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="Video doesn't exist, cannot update")

        if args['name']:
            result.name = args['name']
        if args['views']:
            result.views = args['views']
        if args['likes']:
            result.likes = args['likes']

        db.session.commit()

        return result

    # def delete(self, video_id):
    #     # abort_if_video_doesnt_exist(videoId)
    #     del videos[video_id]
    #     return 'successfully deleted', 204


class HelloWorld(Resource):
    def get(self):
        return {"message": "Malkoto maimunche Lora burka v taratora"}

    def post(self):
        return {"message": "post received"}


api.add_resource(HelloWorld, '/helloworld')
api.add_resource(Video, '/videos/<int:video_id>')
api.add_resource(GetAllVideos, '/videos-all')

if __name__ == '__main__':
    app.run(debug=True)
