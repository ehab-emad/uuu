
def create_root_module():
    from CatiaFramework.models import DotNet_ProjectFolder
    root_component_group = DotNet_ProjectFolder.objects.create(UUID = 'aa4ba40e-8345-4540-8e2f-6afa08c4a8c2', 
                                                                name = 'ROOT', 
                                                                group_depth_level = 0)
    root_component_group.save()
    return root_component_group