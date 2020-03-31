package org.apache.log4j.pattern;

import java.text.DateFormat;
import java.text.FieldPosition;
import java.text.NumberFormat;
import java.text.ParsePosition;
import java.util.Date;
import java.util.TimeZone;

















































































public final class CachedDateFormat
  extends DateFormat
{
  private static final long serialVersionUID = 1L;
  public static final int NO_MILLISECONDS = -2;
  private static final String DIGITS = "0123456789";
  public static final int UNRECOGNIZED_MILLISECONDS = -1;
  private static final int MAGIC1 = 654;
  private static final String MAGICSTRING1 = "654";
  private static final int MAGIC2 = 987;
  private static final String MAGICSTRING2 = "987";
  private static final String ZERO_STRING = "000";
  private final DateFormat formatter;
  private int millisecondStart;
  private long slotBegin;
  private StringBuffer cache = new StringBuffer(50);
  




  private final int expiration;
  




  private long previousTime;
  



  private final Date tmpDate = new Date(0L);
  







  public CachedDateFormat(DateFormat dateFormat, int expiration)
  {
    if (dateFormat == null) {
      throw new IllegalArgumentException("dateFormat cannot be null");
    }
    
    if (expiration < 0) {
      throw new IllegalArgumentException("expiration must be non-negative");
    }
    
    formatter = dateFormat;
    this.expiration = expiration;
    millisecondStart = 0;
    



    previousTime = Long.MIN_VALUE;
    slotBegin = Long.MIN_VALUE;
  }
  









  public static int findMillisecondStart(long time, String formatted, DateFormat formatter)
  {
    long slotBegin = time / 1000L * 1000L;
    
    if (slotBegin > time) {
      slotBegin -= 1000L;
    }
    
    int millis = (int)(time - slotBegin);
    
    int magic = 654;
    String magicString = "654";
    
    if (millis == 654) {
      magic = 987;
      magicString = "987";
    }
    
    String plusMagic = formatter.format(new Date(slotBegin + magic));
    




    if (plusMagic.length() != formatted.length()) {
      return -1;
    }
    
    for (int i = 0; i < formatted.length(); i++) {
      if (formatted.charAt(i) != plusMagic.charAt(i))
      {

        StringBuffer formattedMillis = new StringBuffer("ABC");
        millisecondFormat(millis, formattedMillis, 0);
        
        String plusZero = formatter.format(new Date(slotBegin));
        


        if ((plusZero.length() == formatted.length()) && (magicString.regionMatches(0, plusMagic, i, magicString.length())) && (formattedMillis.toString().regionMatches(0, formatted, i, magicString.length())) && ("000".regionMatches(0, plusZero, i, "000".length())))
        {






          return i;
        }
        return -1;
      }
    }
    


    return -2;
  }
  








  public StringBuffer format(Date date, StringBuffer sbuf, FieldPosition fieldPosition)
  {
    format(date.getTime(), sbuf);
    
    return sbuf;
  }
  










  public StringBuffer format(long now, StringBuffer buf)
  {
    if (now == previousTime) {
      buf.append(cache);
      
      return buf;
    }
    




    if ((millisecondStart != -1) && (now < slotBegin + expiration) && (now >= slotBegin) && (now < slotBegin + 1000L))
    {







      if (millisecondStart >= 0) {
        millisecondFormat((int)(now - slotBegin), cache, millisecondStart);
      }
      



      previousTime = now;
      buf.append(cache);
      
      return buf;
    }
    



    cache.setLength(0);
    tmpDate.setTime(now);
    cache.append(formatter.format(tmpDate));
    buf.append(cache);
    previousTime = now;
    slotBegin = (previousTime / 1000L * 1000L);
    
    if (slotBegin > previousTime) {
      slotBegin -= 1000L;
    }
    




    if (millisecondStart >= 0) {
      millisecondStart = findMillisecondStart(now, cache.toString(), formatter);
    }
    

    return buf;
  }
  







  private static void millisecondFormat(int millis, StringBuffer buf, int offset)
  {
    buf.setCharAt(offset, "0123456789".charAt(millis / 100));
    buf.setCharAt(offset + 1, "0123456789".charAt(millis / 10 % 10));
    buf.setCharAt(offset + 2, "0123456789".charAt(millis % 10));
  }
  






  public void setTimeZone(TimeZone timeZone)
  {
    formatter.setTimeZone(timeZone);
    previousTime = Long.MIN_VALUE;
    slotBegin = Long.MIN_VALUE;
  }
  






  public Date parse(String s, ParsePosition pos)
  {
    return formatter.parse(s, pos);
  }
  




  public NumberFormat getNumberFormat()
  {
    return formatter.getNumberFormat();
  }
  











  public static int getMaximumCacheValidity(String pattern)
  {
    int firstS = pattern.indexOf('S');
    
    if ((firstS >= 0) && (firstS != pattern.lastIndexOf("SSS"))) {
      return 1;
    }
    
    return 1000;
  }
}
