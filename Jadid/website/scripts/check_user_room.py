from website.models import Room
def check_user_room(userobj) -> Room:
    """
    This function checks if active ProjectUser has available Room and if not will add it and join the user to the room
    """
    if not userobj.is_authenticated:
        return None 
    new_room = Room.objects.filter(name = userobj.username) 
    if new_room:
        new_room = new_room.get() 
    else:    
        new_room = Room.objects.create(name = userobj.username )

    new_room.owner = userobj
    new_room.join(userobj)
    new_room.save()

    return new_room