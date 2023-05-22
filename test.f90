program test
  use datafitPde
  implicit none

  real :: out(3690)
  real(8) :: D, R, volPer, iapp, F, L, Rg, T, K, maxCon, dt
  real(8), dimension(:), allocatable :: c0
  integer(4):: n, totaltime
  n = 20
  totaltime= 3690
  D = 1.48e-15 
  R = 5.22e-6
  volPer = 66.5
  iapp = 0.001
  F = 96485.3
  L = 75.6e-6
  Rg = 8.31
  T = 294.15
  K = 3.24
  maxCon = 51765.0
  dt = 1
  allocate(c0(20))
  c0 = 1000.0
  out = crank_nicholson(n, totaltime, D, R, volPer, iapp, F, L, Rg, T, K, maxCon, c0, dt)
  print *, out
  deallocate(c0)

end program