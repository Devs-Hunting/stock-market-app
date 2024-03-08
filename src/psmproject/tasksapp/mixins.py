from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


class InstanceChatDetailsMixin:
    chat_model = None

    def chat_context_data(self):
        try:
            return {"chat_id": self.chat_model.objects.get(object_id=self.object.id).id}
        except ObjectDoesNotExist:
            messages.add_message(
                self.request,
                messages.WARNING,
                "No chat related to this task was found, please contact the administrator.",
            )
        except MultipleObjectsReturned:
            messages.add_message(
                self.request,
                messages.WARNING,
                "More than one chat was found for this task, please contact the administrator.",
            )
