

class Page(object):
       def __init__(self,item_count,page_index=1,page_size=10):
           self.item_count=item_count
           self.page_size=page_size
           self.page_count=item_count//page_size + (1 if item_count%page_size>0 else 0)

           if(item_count==0) or (page_index>self.page_count):
                self.offset=0
                self.limit=0
                self.page_index=1
           else:
                  self.page_index=1
                  self.offset=self.page_size*(page_index-1)
                  self.limit=self.page_size
           self.has_next=self.page_index<self.page_count
           self.has_previous=self.page_index>1

       def __str__(self):
               return 'item_count: %s,page_size: %s,page_count: %s,has_next: %s,has_previous: %s'  % ( self.item_count,self.page_size,self.page_count,self.has_next,self.has_previous)
       __repr__=__str__