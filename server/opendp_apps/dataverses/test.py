import requests as r


def make_request():
      return r.post('http://localhost:8000/dv-test/dv-info/get-user-info',
                  params={'site_url': 'https://dataverse.harvard.edu', 'apiGeneralToken': '920b1f22-8fad-4351-bb1b-a44c3e929213'})


if __name__ == '__main__':
      print(make_request().content)