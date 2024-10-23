import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(advancedFormat);

export const formatTimestamp = (
  date: string,
  options?: { showTime?: boolean },
) => {
  if (options?.showTime) {
    return dayjs(date).format("MMM D, YYYY h:mm A z");
  }
  return dayjs(date).format("MMM D, YYYY");
};
