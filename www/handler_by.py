

class Page(object):
       def __init__(self,item_count,page_index=1,page_size=10):
           self.item_count=item_count
           self.page_size=page_size
           self.page_count=item_count//page_size + (1 if item_count%page_size>0 else 0)

           if(item_count==0) :
                self.offset=0
                self.limit=0
                self.page_index=1
           elif page_index>self.page_count:
                self.page_index=self.page_count
                self.offset = self.page_size * (self.page_index - 1)
                self.limit = self.page_size
           else:
                  self.page_index=page_index
                  self.offset=self.page_size*(page_index-1)
                  self.limit=self.page_size
           self.has_next=(1 if self.page_index<self.page_count else 0)
           self.has_previous= (1 if self.page_index>1 else 0)

       def __str__(self):
               return 'item_count: %s,page_size: %s,page_count: %s,has_next: %s,has_previous: %s,page_index: %s'  % ( self.item_count,self.page_size,self.page_count,self.has_next,self.has_previous,self.page_index)
       __repr__=__str__
