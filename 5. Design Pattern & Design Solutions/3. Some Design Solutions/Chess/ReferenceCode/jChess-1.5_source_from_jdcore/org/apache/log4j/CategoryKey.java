package org.apache.log4j;








class CategoryKey
{
  String name;
  






  int hashCache;
  







  CategoryKey(String name)
  {
    this.name = name;
    hashCache = name.hashCode();
  }
  

  public final int hashCode()
  {
    return hashCache;
  }
  

  public final boolean equals(Object rArg)
  {
    if (this == rArg) {
      return true;
    }
    if ((rArg != null) && (CategoryKey.class == rArg.getClass())) {
      return name.equals(name);
    }
    return false;
  }
}
