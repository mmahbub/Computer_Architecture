#include <emmintrin.h>
#include <stdio.h>

float dotprod(float x[], float y[], int n)
{
  int i;
  float total;

  __m128 num1, num2, num3, num4;
  num4 = _mm_set1_ps(0.0f);

  for(i=0; i<n; i+=4)
  {
    num1 = _mm_load_ps(x+i);
    num2 = _mm_load_ps(y+i);
    num3 = _mm_mul_ps(num1, num2);
    num3 = _mm_add_ps(num3, num3);
    num4 = _mm_add_ps(num4, num3);
  }
  num4= _mm_add_ps(num4, num4);
  _mm_store_ps(&total,num4);
  return total;

}
