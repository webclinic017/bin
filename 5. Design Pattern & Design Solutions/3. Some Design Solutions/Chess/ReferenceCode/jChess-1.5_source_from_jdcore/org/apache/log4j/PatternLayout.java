package org.apache.log4j;

import org.apache.log4j.helpers.PatternConverter;
import org.apache.log4j.helpers.PatternParser;
import org.apache.log4j.spi.LoggingEvent;


















































































































































































































































































































































































































public class PatternLayout
  extends Layout
{
  public static final String DEFAULT_CONVERSION_PATTERN = "%m%n";
  public static final String TTCC_CONVERSION_PATTERN = "%r [%t] %p %c %x - %m%n";
  protected final int BUF_SIZE = 256;
  protected final int MAX_CAPACITY = 1024;
  


  private StringBuffer sbuf = new StringBuffer(256);
  

  private String pattern;
  

  private PatternConverter head;
  


  public PatternLayout()
  {
    this("%m%n");
  }
  


  public PatternLayout(String pattern)
  {
    this.pattern = pattern;
    head = createPatternParser(pattern == null ? "%m%n" : pattern).parse();
  }
  






  public void setConversionPattern(String conversionPattern)
  {
    pattern = conversionPattern;
    head = createPatternParser(conversionPattern).parse();
  }
  



  public String getConversionPattern()
  {
    return pattern;
  }
  






  public void activateOptions() {}
  






  public boolean ignoresThrowable()
  {
    return true;
  }
  






  protected PatternParser createPatternParser(String pattern)
  {
    return new PatternParser(pattern);
  }
  




  public String format(LoggingEvent event)
  {
    if (sbuf.capacity() > 1024) {
      sbuf = new StringBuffer(256);
    } else {
      sbuf.setLength(0);
    }
    
    PatternConverter c = head;
    
    while (c != null) {
      c.format(sbuf, event);
      c = next;
    }
    return sbuf.toString();
  }
}
