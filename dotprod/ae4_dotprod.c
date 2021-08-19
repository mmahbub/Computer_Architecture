float dotprod(float x[], float y[], int n)
{
   int i;
   float sum1, sum2, sum3, sum4, finalsum;

   sum1 = 0.0;
   sum2 = 0.0;
   sum3 = 0.0;
   sum4 = 0.0;
   finalsum = 0.0;
   for (i = 0; i<n; i+=4){
      sum1 += x[i] * y[i];
      sum2 += x[i+1] * y[i+1];
      sum3 += x[i+2] * y[i+2];
      sum4 += x[i+3] * y[i+3];
   }
   finalsum = sum1 + sum2 + sum3 + sum4;
   return finalsum;
}
