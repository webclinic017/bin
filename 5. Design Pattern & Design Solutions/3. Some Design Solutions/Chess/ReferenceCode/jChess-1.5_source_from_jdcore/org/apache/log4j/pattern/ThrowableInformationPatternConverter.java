package org.apache.log4j.pattern;

import org.apache.log4j.spi.LoggingEvent;
import org.apache.log4j.spi.ThrowableInformation;

































public class ThrowableInformationPatternConverter
  extends LoggingEventPatternConverter
{
  private int maxLines = Integer.MAX_VALUE;
  




  private ThrowableInformationPatternConverter(String[] options)
  {
    super("Throwable", "throwable");
    
    if ((options != null) && (options.length > 0)) {
      if ("none".equals(options[0])) {
        maxLines = 0;
      } else if ("short".equals(options[0])) {
        maxLines = 1;
      } else {
        try {
          maxLines = Integer.parseInt(options[0]);
        }
        catch (NumberFormatException ex) {}
      }
    }
  }
  






  public static ThrowableInformationPatternConverter newInstance(String[] options)
  {
    return new ThrowableInformationPatternConverter(options);
  }
  


  public void format(LoggingEvent event, StringBuffer toAppendTo)
  {
    if (maxLines != 0) {
      ThrowableInformation information = event.getThrowableInformation();
      
      if (information != null) {
        String[] stringRep = information.getThrowableStrRep();
        
        int length = stringRep.length;
        if (maxLines < 0) {
          length += maxLines;
        } else if (length > maxLines) {
          length = maxLines;
        }
        
        for (int i = 0; i < length; i++) {
          String string = stringRep[i];
          toAppendTo.append(string).append("\n");
        }
      }
    }
  }
  



  public boolean handlesThrowable()
  {
    return true;
  }
}
