from django import forms


class ContactForm(forms.Form):
    name=forms.CharField(required=False)
    email=forms.EmailField(required=False)
    message=forms.CharField(required=False)

   