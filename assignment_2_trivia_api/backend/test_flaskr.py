import os
import json
import unittest
from http import HTTPStatus
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    question_id = None

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432',
                                                         self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.categories = {'1': 'Science',
                           '2': 'Art',
                           '3': 'Geography',
                           '4': 'History',
                           '5': 'Entertainment',
                           '6': 'Sports'
                           }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories_success(self):
        response = self.client().get('/categories')
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual({'categories': self.categories}, response.json)

    def test_get_all_questions_success(self):
        response = self.client().get('/questions?page=2')
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertGreaterEqual(response.json.get('total_questions'), 0)
        self.assertEqual(type(response.json.get('questions')), list)
        self.assertEqual(response.json.get('categories'), self.categories)

    def test_create_question_success(self):
        new_question = {
            "question": "Test new question",
            "answer": "Test new answer",
            "category": 5,
            "difficulty": 2
        }
        response = self.client().post('/questions', json=new_question)
        self.assertEqual(HTTPStatus.CREATED, response.status_code)
        self.question_id = response.json.get('id')

    def test_create_question_fail(self):
        response = self.client().post('/questions/12', json={})
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)

    def test_delete_question_success(self):
        response = self.client().delete(f'/questions/{self.question_id}')
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

    def test_delete_question_fail(self):
        response = self.client().delete('/questions/100')
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_search_questions_success(self):
        data = {
            "searchTerm": "your search string"
        }
        response = self.client().post('/questions/search', json={})
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(type(response.json.get('questions')), list)
        self.assertEqual(type(response.json.get('total_questions')), int)

    def test_search_questions_fail(self):
        response = self.client().post('/questions/searchs', json={})
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_get_category_questions_success(self):
        response = self.client().get('/categories/1/questions')
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_get_category_questions_fail(self):
        response = self.client().get('/categories/30/question')
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_get_next_questions_success(self):
        data = {
            'quiz_category': {'type': 'Sports', 'id': '6'},
            'previous_questions': [3, 1, 23, 9]
        }
        response = self.client().post('/quizzes', json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_get_next_questions_fail(self):
        response = self.client().post('/quizzes', json={})
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
