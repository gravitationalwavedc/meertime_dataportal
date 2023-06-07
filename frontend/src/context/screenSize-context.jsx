import React from "react";

const ScreenSizeContext = React.createContext({});

/* eslint-disable complexity */
const bootstap4Breakpoints = (width) => {
  if (width >= 1440) return "xxl"; // not support by bootstrap4. Only used in the tables.
  if (width >= 1200) return "xl";
  if (width >= 992) return "lg";
  if (width >= 768) return "md";
  if (width >= 576) return "sm";
  return "xs";
};

export const ScreenSizeProvider = ({ children }) => {
  const [width, setWidth] = React.useState(window.innerWidth);
  const [height, setHeight] = React.useState(window.innerHeight);
  const [screenSize, setScreenSize] = React.useState(
    bootstap4Breakpoints(window.innerWidth)
  );

  const handleWindowResize = () => {
    setWidth(window.innerWidth);
    setHeight(window.innerHeight);
    setScreenSize(bootstap4Breakpoints(window.innerWidth));
  };

  React.useEffect(() => {
    window.addEventListener("resize", handleWindowResize);
    return () => window.removeEventListener("resize", handleWindowResize);
  }, []);

  /* Now we are dealing with a context instead of a Hook, so instead
     of returning the width and height we store the values in the
     value of the Provider */
  return (
    <ScreenSizeContext.Provider value={{ width, height, screenSize }}>
      {children}
    </ScreenSizeContext.Provider>
  );
};

/* Rewrite the "useViewport" hook to pull the width and height values
   out of the context instead of calculating them itself */
export const useScreenSize = () => {
  /* We can use the "useContext" Hook to acccess a context from within
     another Hook, remember, Hooks are composable! */
  const { width, height, screenSize } = React.useContext(ScreenSizeContext);
  return { width, height, screenSize };
};
