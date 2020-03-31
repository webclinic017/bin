package org.apache.log4j;

import java.io.IOException;
import java.io.InterruptedIOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import org.apache.log4j.helpers.LogLog;
import org.apache.log4j.helpers.QuietWriter;
import org.apache.log4j.spi.ErrorHandler;
import org.apache.log4j.spi.LoggingEvent;










































public class WriterAppender
  extends AppenderSkeleton
{
  protected boolean immediateFlush = true;
  




  protected String encoding;
  




  protected QuietWriter qw;
  





  public WriterAppender() {}
  





  public WriterAppender(Layout layout, OutputStream os)
  {
    this(layout, new OutputStreamWriter(os));
  }
  






  public WriterAppender(Layout layout, Writer writer)
  {
    this.layout = layout;
    setWriter(writer);
  }
  














  public void setImmediateFlush(boolean value)
  {
    immediateFlush = value;
  }
  



  public boolean getImmediateFlush()
  {
    return immediateFlush;
  }
  














  public void activateOptions() {}
  














  public void append(LoggingEvent event)
  {
    if (!checkEntryConditions()) {
      return;
    }
    subAppend(event);
  }
  






  protected boolean checkEntryConditions()
  {
    if (closed) {
      LogLog.warn("Not allowed to write to a closed appender.");
      return false;
    }
    
    if (qw == null) {
      errorHandler.error("No output stream or file set for the appender named [" + name + "].");
      
      return false;
    }
    
    if (layout == null) {
      errorHandler.error("No layout set for the appender named [" + name + "].");
      return false;
    }
    return true;
  }
  










  public synchronized void close()
  {
    if (closed)
      return;
    closed = true;
    writeFooter();
    reset();
  }
  


  protected void closeWriter()
  {
    if (qw != null) {
      try {
        qw.close();
      } catch (IOException e) {
        if ((e instanceof InterruptedIOException)) {
          Thread.currentThread().interrupt();
        }
        

        LogLog.error("Could not close " + qw, e);
      }
    }
  }
  






  protected OutputStreamWriter createWriter(OutputStream os)
  {
    OutputStreamWriter retval = null;
    
    String enc = getEncoding();
    if (enc != null) {
      try {
        retval = new OutputStreamWriter(os, enc);
      } catch (IOException e) {
        if ((e instanceof InterruptedIOException)) {
          Thread.currentThread().interrupt();
        }
        LogLog.warn("Error initializing output writer.");
        LogLog.warn("Unsupported encoding?");
      }
    }
    if (retval == null) {
      retval = new OutputStreamWriter(os);
    }
    return retval;
  }
  
  public String getEncoding() {
    return encoding;
  }
  
  public void setEncoding(String value) {
    encoding = value;
  }
  





  public synchronized void setErrorHandler(ErrorHandler eh)
  {
    if (eh == null) {
      LogLog.warn("You have tried to set a null error-handler.");
    } else {
      errorHandler = eh;
      if (qw != null) {
        qw.setErrorHandler(eh);
      }
    }
  }
  











  public synchronized void setWriter(Writer writer)
  {
    reset();
    qw = new QuietWriter(writer, errorHandler);
    
    writeHeader();
  }
  








  protected void subAppend(LoggingEvent event)
  {
    qw.write(layout.format(event));
    
    if (layout.ignoresThrowable()) {
      String[] s = event.getThrowableStrRep();
      if (s != null) {
        int len = s.length;
        for (int i = 0; i < len; i++) {
          qw.write(s[i]);
          qw.write(Layout.LINE_SEP);
        }
      }
    }
    
    if (shouldFlush(event)) {
      qw.flush();
    }
  }
  






  public boolean requiresLayout()
  {
    return true;
  }
  





  protected void reset()
  {
    closeWriter();
    qw = null;
  }
  





  protected void writeFooter()
  {
    if (layout != null) {
      String f = layout.getFooter();
      if ((f != null) && (qw != null)) {
        qw.write(f);
        qw.flush();
      }
    }
  }
  



  protected void writeHeader()
  {
    if (layout != null) {
      String h = layout.getHeader();
      if ((h != null) && (qw != null)) {
        qw.write(h);
      }
    }
  }
  




  protected boolean shouldFlush(LoggingEvent event)
  {
    return immediateFlush;
  }
}
