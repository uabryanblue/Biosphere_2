# common functions for LICOR-LOGS project

read_and_clean_data <- function(filename) {
  # TODO this fails unless r is restarted first! WHY?
  # fname <- here(DATAUSER, "final_raw_data.csv")
  finaldata <- read_csv(filename, # "final_raw_data.csv"
                        col_names = TRUE, 
                        show_col_types = FALSE) 
  
  # change any value in the df that is < zero to NA, invalid data
  finaldata[finaldata < 0] <- NA
  
  # try to auto convert all data types, not all work
  finaldata <- type.convert(finaldata, as.is = TRUE)
  # convert values that were not correctly auto converted
  # TODO add in the type cleanup code, or new function
  finaldata$Data_leaftype <- as.factor(finaldata$Data_leaftype)
  finaldata$Filenames_filename <- as.factor(finaldata$Filenames_filename)
  finaldata$Data_plant_id <- as.factor(finaldata$Data_plant_id)
  
  # NOTE: this observation is turned into a date, not date/time, this is not correct
  # are new variable for "date" needs added
  # finaldata$SysObs_date <-  as.POSIXct(finaldata$SysObs_date, format = "%Y%m%d %H:%M:%S")
  finaldata$SysObs_date <- as.Date(finaldata$SysObs_date)
  
  # only interested in values for this experiment
  finaldata <- finaldata %>% 
    filter(Data_leaftype == "Treatment" |
             Data_leaftype == "Control" |
             Data_leaftype == "Reference") 
  
  # The clock was off at one point, this needs corrected or ignore the values
  finaldata <- finaldata %>% filter(SysObs_time > 1668543540) %>% arrange(SysObs_date)
  
  return(finaldata)
}



