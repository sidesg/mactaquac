from django import forms

class MediaFileSearchForm(forms.Form):
    item_identifier = forms.CharField(label="item identifier", max_length=55, required=False)
    collection = forms.CharField(label="collection", max_length=15, required=False)
    title = forms.CharField(label="item title", max_length=255, required=False)
    filename = forms.CharField(label="filename", required=False)
