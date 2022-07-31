## API Reference

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 
- 500: Internal Server Error

### Endpoints 

#### GET /categories
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

#### GET /questions?page=<int:page_key>
- Fetches a paginated set of questions, a total number of questions, all categories and current category string.
- Request Arguments: `page` - integer
- Returns: An object with 10 paginated questions, total questions, object including all categories, and current category string
```json
{
  "questions": [
    {
      "id": 3,
      "question": "Test question",
      "answer": "Test answer",
      "difficulty": 1,
      "category": 4
    },
    ...
  ],
  "total_questions": 23,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": "Art"
}
```

#### POST /questions
- Sends a post request in order to add a new question
- Request Body:
```json
{
  "question": "Test new question",
  "answer": "Test new answer",
  "category": 5,
  "difficulty": 2
}
```
- Returns: HTTP Status: 201 (Created)

#### POST /questions/search
- Sends a post request in order to search for a specific question by search term
- Request Body:
```json
{
  "searchTerm": "your search string"
}
```

- Returns: any array of questions, a number of total_questions that met the 
  search term and the current category string
```json
{
  "questions": [
    {
      "id": 7,
      "question": "Test question",
      "answer": "Test answer",
      "difficulty": 3,
      "category": 2
    },
    ...
  ],
  "total_questions": 15,
  "current_category": "Sports"
}
```

#### DELETE /questions/<int:question_id>
- Deletes a specified question using the id of the question
- Request Arguments: `question_id` - integer
- Returns: HTTP Status 204 (No Content)

#### GET /categories/<string:category_id>/questions
- Fetches questions for a cateogry specified by id request argument
- Request Arguments: `category_id` - integer
- Returns: An object with questions for the specified category, total questions, and current category string
```json
{
  "questions": [
    {
      "id": 1,
      "question": "Test question",
      "answer": "Test answer",
      "difficulty": 2,
      "category": 3
    }
  ],
  "total_questions": 35,
  "current_category": "Art"
}
```

#### POST /quizzes
- Sends a post request in order to get the next question
- Request Body:
```json
{
    quiz_category': 'Sports',
    'previous_questions': [3, 1, 23, 9]
 }
```

- Returns: a single new question object
```json
{
  "question": {
    "id": 8,
    "question": "Test question",
    "answer": "Test answer",
    "difficulty": 3,
    "category": 2
  }
}
```
