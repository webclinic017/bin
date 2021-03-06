package org.apache.log4j.helpers;

import java.io.IOException;
import java.io.Writer;
import org.apache.log4j.spi.ErrorHandler;


























public class CountingQuietWriter
  extends QuietWriter
{
  protected long count;
  
  public CountingQuietWriter(Writer writer, ErrorHandler eh)
  {
    super(writer, eh);
  }
  
  public void write(String string)
  {
    try {
      out.write(string);
      count += string.length();
    }
    catch (IOException e) {
      errorHandler.error("Write failure.", e, 1);
    }
  }
  
  public long getCount()
  {
    return count;
  }
  
  public void setCount(long count)
  {
    this.count = count;
  }
}
