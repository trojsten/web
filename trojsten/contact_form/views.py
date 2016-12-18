import contact_form.views

from .forms import ContactForm


class ContactFormView(contact_form.views.ContactFormView):
    form_class = ContactForm

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(ContactFormView, self).get_initial()
        if self.request.user.is_anonymous():
            return initial

        initial['name'] = self.request.user.get_full_name()
        initial['email'] = self.request.user.email
        return initial
