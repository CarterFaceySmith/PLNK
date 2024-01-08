import React, { useState } from "react";
import { Box, Button, Typography, useTheme } from "@mui/material";

const Homepage: React.FC = () => {
  const { palette } = useTheme();
  const [isPredictions, setIsPredictions] = useState(false);

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height="100vh"
    >
    <Typography variant="h1" gutterBottom>
    PLNK
    </Typography>
    <Typography variant="h2" gutterBottom>
        Quantitative microfund.
    </Typography>
    </Box>
  );
};

export default Homepage;
