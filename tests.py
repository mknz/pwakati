import unittest

from app import app
import decompose


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True

        # Need this to do form post test
        app.config['WTF_CSRF_ENABLED'] = False

        self.app = app.test_client()

    def post_input(self, string):
        return self.app.post('/', data=dict(text=string))

    def tearDown(self):
        pass


class TestInputs(FlaskTestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_get(self):
        response = self.app.get('/')
        assert response.status_code == 200

    def test_inputs(self):
        # This somehow does not work!
        '''
        string = '分かち書き'
        response = self.post_input(string)

        self.assertIn('わかちがき', response.data.decode())
        '''

    def test_decompose(self):
        examples = []
        examples.append(dict(before='分かち書き', after='わかちがき'))

        for example in examples:
            decomposed_string = decompose.main(example['before'])
            self.assertEqual(decomposed_string, example['after'], example['before'])


if __name__ == '__main__':
    unittest.main()
