from rest_auth.views import UserDetailsView


class CustomUserDetailsView(UserDetailsView):
    """Handle the user data of currently logged-in user.

    get:

    Return details of the currently logged in user.

    ### Response

    #### Example response data:

        {
            "id": 1,
            "description": "Lorem ipsum",
            "email": "john.doe@example.com",
            "expose_email_address": False,
            "facebook_url": "",
            "first_name": "John",
            "full_name": "John Doe",
            "image_url": "http://testserver/media/test.jpeg",
            "instagram_url": "",
            "interested_in_themes": [
                {
                    "id": 1,
                    "name": "Theme",
                    "is_curated": False,
                }
            ],
            "last_name": "Doe",
            "linkedin_url": "",
            "looking_for": [
                {
                    "id": 1,
                    "value": "Help",
                }
            ],
            "status": {
                "id": 1,
                "value": "Student",
            },
            "twitter_url": ""
        }

    put:

    Update user information of the currently logged in user.

    ### Notices

    - Possible values for `language` field are `fi`, `sv` and `en`.

    ### Request

    #### Example request data:

        {
            "description": "Lorem ipsum",
            "expose_email_address": True,
            "facebook_url": "",
            "first_name": "John",
            "image_id": 1,
            "instagram_url": "",
            "interested_in_theme_ids": [
                1
            ],
            "language": "fi",
            "last_name": "Doe",
            "linkedin_url": "",
            "looking_for_ids": [
                1
            ],
            "status_id": 1,
            "twitter_url": ""
        }

    ### Response

    #### Example response data:

        {
            "id": 1,
            "description": "Lorem ipsum",
            "email": "john.doe@example.com",
            "expose_email_address": True,
            "facebook_url": "",
            "first_name": "John",
            "full_name": "John Doe",
            "image_url": "http://testserver/media/test.jpeg",
            "instagram_url": "",
            "interested_in_themes": [
                {
                    "id": 1,
                    "name": "Theme",
                    "is_curated": False,
                }
            ],
            "last_name": "Doe",
            "linkedin_url": "",
            "looking_for": [
                {
                    "id": 1,
                    "value": "Help",
                }
            ],
            "status": {
                "id": 1,
                "value": "Student",
            },
            "twitter_url": ""
        }

    patch:

    Update some user information fields of the currently logged in user.

    ### Notices

    - Possible values for `language` field are `fi`, `sv` and `en`.

    ### Request

    #### Example request data:

        {
            "description": "Lorem ipsum",
        }

    ### Response

    #### Example response data:

        {
            "id": 1,
            "description": "Lorem ipsum",
            "email": "john.doe@example.com",
            "expose_email_address": True,
            "facebook_url": "",
            "first_name": "John",
            "full_name": "John Doe",
            "image_url": "http://testserver/media/test.jpeg",
            "instagram_url": "",
            "interested_in_themes": [
                {
                    "id": 1,
                    "name": "Theme",
                    "is_curated": False,
                }
            ],
            "last_name": "Doe",
            "linkedin_url": "",
            "looking_for": [
                {
                    "id": 1,
                    "value": "Help",
                }
            ],
            "status": {
                "id": 1,
                "value": "Student",
            },
            "twitter_url": ""
        }

    """
