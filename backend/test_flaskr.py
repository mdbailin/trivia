import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            'question': 'Who is the man?',
            'answer': 'You are!',
            'category': 5,
            'difficulty': 3
        }
        self.bad_question = {
            'question': 'Is this question unfinished?',
            'answer': 'Yes, it is.'
        }

        self.quiz_question = {
            'previous_questions': [2, 3, 5, 7],
            'quiz_category': 'Art',
            'question': self.new_question
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #Test Get Categories
    def test_get_categories(self):
        """Tests whether we get categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['all_categories'])
        self.assertTrue(len(data['categories']))
    
    def test_404_no_valid_category(self):
        """tests whether a 404 error occurs if we make an invalid category request"""
        res = self.client().get('/categorie')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not found')
    
    #test GET questions
    def test_get_questions(self):
        """tests whether we get questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_no_valid_questions(self):
        """Tests whether a 404 error occurs if we request an invalid page"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not found')

        self.assertEqual(res.status_code, 404)

    #test DELETE questions
    def test_delete_question(self):
        """Tests whether a question is deleted"""
        res = self.client().delete('questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_delete_if_question_does_not_exist(self):
        """Tests whether a 422 error occurs if we try to delete a question that doesn't exist"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

        self.assertEqual(res.status_code, 422)
    
    #test CREATE question
    def test_create_new_questions(self):
        """tests whether we can create a new question"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        question = Question.query.filter(Question.question == self.new_question['question']).first()

        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertTrue(question)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_422_if_create_question_not_allowed(self):
        """Tests if a 404 error occurs if we make a bad question post"""
        res = self.client().post('/questions/', json=self.bad_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    #test SEARCH questions
    def test_search_questions(self):
        """tests whether we can successfully search for questions"""
        res = self.client().post('/questions', json={'searchTerm': 'movie'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_if_searchTerm_does_not_exist(self):
        """tests that no search results are found"""
        res = self.client().post('/questions', json={'searchTerm': 'video games'})
        data = json.loads(res.data)

        questions = Question.query \
            .order_by(Question.id) \
            .filter(Question.question.ilike('%video games%')) \
            .all()

        format_questions = [question.format() for question in questions]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], format_questions)
        self.assertEqual(len(data['questions']), len(questions))
        self.assertEqual(data['searchTerm'], 'video games')

    #test GET questions based on category

    def test_get_questions_based_on_category(self):
        """tests whether we get questions based on a category"""
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'History')
    
    def test_404_if_selected_category_not_found(self):
        """tests whether a 404 error occurs if the category doesn't exist"""
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    #test PLAY quiz
    def test_play_quiz(self):
        """Tests whether a quiz based on a category"""
        res = self.client().post('/quizzes', json={
            "quiz_category": {"type": "Art", "id": 2},
            "previous_questions": [],
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))

    def test_422_if_quiz_bad(self):
        """tests whether a 422 error occurs if the quiz is bad"""
        res = self.client().post('/quizzes', json=self.quiz_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()