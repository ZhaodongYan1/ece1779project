import requests
import re
URL = 'https://services.gingersoftware.com/Ginger/correct/jsonSecured/GingerTheTextFull'  # noqa
API_KEY = '6ae0c3a0-afdc-4532-a810-82ded0054236'


class GingerIt(object):
    def __init__(self):
        self.url = URL
        self.api_key = API_KEY
        self.api_version = '2.0'
        self.lang = 'US'

    def parse(self, text):
        session = requests.Session()
        request = session.get(
            self.url,
            params={
                'lang': self.lang,
                'apiKey': self.api_key,
                'clientVersion': self.api_version,
                'text': text
            },
        )
        data = request.json()
        return self._process_data(text, data)

    @staticmethod
    def _change_char(original_text, from_position, to_position, change_with):
        return "{}{}{}".format(original_text[:from_position],
                               change_with,
                               original_text[to_position + 1:])

    def _process_data(self, text, data):
        result = text
        colored_result=text
        original_text=text
        corrections = []

        for suggestion in reversed(data['Corrections']):
            start = suggestion["From"]
            end = suggestion["To"]

            if suggestion['Suggestions']:
                suggest = suggestion['Suggestions'][0]
                regex = re.compile("[@_!#$%^&*()<>?/\|}{~:']")
                if not result[start].islower():
                    if regex.search(result[start:end]) == None:
                        continue
                # Colorize text


                original_text = original_text[:start] +  "<span style='background-color:red'>"+result[start:end+1] + "</span>"+ original_text[end+1:]
                colored_result = colored_result[:start] +  "<span style='background-color:green'>"+ suggest['Text']+ "</span>"+ colored_result[end+1:]


                result = self._change_char(result, start, end, suggest['Text'])
                corrections.append({
                    'start':start,
                    'text': text[start:end+1],
                    'correct': suggest.get('Text', None),
                    'definition': suggest.get('Definition', None)
                })

        return {'text': text, 'result': result, 'corrections': corrections,'color_t':original_text, 'color_r':colored_result}




if __name__ == '__main__':
    results=GingerIt().parse('I hates you but I had to loved you')
