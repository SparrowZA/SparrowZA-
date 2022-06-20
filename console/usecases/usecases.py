from datetime import date, datetime
from http import client

# Models
from console.adapters.django_storage import DjangoStorage

# Helper functions
from console.utils.authentication_utils import get_user_Id
from console.utils.serializer import build_console_table_list
from console.utils.email_utils import EmailBuilder

class Usecases:
    def __init__(self):
        self.storage = DjangoStorage()

    def login(self, form):
        rm_email = form['email']
        return get_user_Id(rm_email)

    def create_client_usecase(self, form_data):
        '''
            Takes the form data creates a client entity and saves the data via 
            the storage interface -> Currently using the Django ORM.
        '''
        # TODO: Check if form_data is clean
        name = form_data['client_name']
        email = form_data['client_email']
        company = form_data['client_company']
        return self.storage.create_client(name=name, company=company, email=email)
    
    def get_client_list(self):
        '''
            Returns a object list of client entities from the storage interface.
        '''
        client_list = self.storage.get_clients()
        form = {
            'client_list': client_list
        }
        return form
    
    def create_request_usecase(self, form_data, rm_id):
        '''
            Function takes form data and creates a document request.
            It sends a notification to the client and save the request
            to the storage interface.
        '''
        client = self.storage.get_client(client_id=form_data['client'])
        rm = self.storage.get_rm(rm_id=rm_id)
        request_date = datetime.now()
        request = self.storage.create_request(
            request_date=request_date,
            submitted=False,
            doc_name=form_data['doc_name'],
            relationship_manager=rm,
            client=client
            )
        
        # TODO: Send email notification
        email_builder = EmailBuilder(client, request)
        email = email_builder.build_request_email()

        return request
    
    def get_request_list(self):
        '''
            Returns an array of formatted objects for the views table.
        '''
        requests = self.storage.get_requests()
        console_list = build_console_table_list(requests)
        # f = requests.document
        return console_list
    
    def is_client_url_active(self, client_url) -> bool:
        ''' Takes the client url UUID as an argument and checks if it is still
        active.
        '''
        request = self.storage.get_request_by_url(client_url)
        if request is None or request.submitted == True:
            return False
        else:
            return True
    
    def get_client_by_url(self, client_url):
        ''' Takes the client url UUID as an argument, gets the request associated
        to that url and returns the request's client entity.
        '''
        request = self.storage.get_request_by_url(client_url)
        return request.client.to_dict()

    def upload_client_file(self, file, client_url):
        request = self.storage.get_request_by_url(client_url=client_url)
        doc_upload = self.storage.create_document(
            request=request,
            file=file
            )
        request.submitted = True
        self.storage.update_request_submit(request.id, True)
        self.storage.update_request(request)
        return doc_upload
