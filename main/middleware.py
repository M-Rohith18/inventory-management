from django.urls import reverse
from django.shortcuts import redirect

# ITEM LIST
class redirectauthenticatedusermiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self,request):
        if request.user.is_authenticated:
            path_to_redirect = [reverse("inventory_project:login"),reverse("inventory_project:register"),reverse("inventory_project:forget_password")]
            if request.path in  path_to_redirect:
                return redirect(reverse("inventory_project:item_list"))
        response = self.get_response(request)
        return response
    
class restrictunauthenticatedusermiddleware:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        if not request.user.is_authenticated:
            path_to_restrict = [reverse("inventory_project:item_list"),
                                reverse("inventory_project:add_category"),
                                reverse("inventory_project:add_new_item"),
                                reverse("inventory_project:add_reduce"),
                                reverse("inventory_project:transaction"),
                                reverse("inventory_project:download"),]
            if request.path in path_to_restrict:
                return redirect (reverse("inventory_project:login"))
        response = self.get_response(request)
        return response
    

 
    
    